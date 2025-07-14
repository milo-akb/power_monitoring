#!/bin/bash

sleep_interval=0.5
output_file="rapl_power_log.csv"
run_duration=0

# Parse optional duration argument
if [[ $# -ge 1 && "$1" =~ ^[0-9]+$ ]]; then
    run_duration="$1"
elif [[ $# -ge 1 ]]; then
    echo "Usage: $0 [run_duration_seconds]"
    exit 1
fi

running=true
trap 'running=false' SIGINT SIGTERM

# Detect max energy range
detect_max_val() {
    local dir="$1"
    local file="$dir/max_energy_range_uj"
    [[ -f "$file" ]] && cat "$file" || echo $((1<<32))
}

# Get initial RAPL domains and names
rapl_domains=()
rapl_names=()
for dir in /sys/class/powercap/intel-rapl:[0-9]*; do
    base=$(basename "$dir")
    [[ "$base" =~ ^intel-rapl:[0-9]+$ ]] || continue
    [[ -f "$dir/energy_uj" ]] || continue
    rapl_domains+=("$dir")
    if [[ -f "$dir/name" ]]; then
        name=$(<"$dir/name")
        [[ -z "$name" ]] && name="unknown"
        rapl_names+=("$name")
    else
        rapl_names+=("unknown")
    fi
done

[[ ${#rapl_domains[@]} -eq 0 ]] && echo "No RAPL domains found!" && exit 1

max_val=$(detect_max_val "${rapl_domains[0]}")

# Frequency, governor, pstate utils
get_current_governor() {
    cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "unknown"
}
get_pstate_status() {
    cat /sys/devices/system/cpu/intel_pstate/status 2>/dev/null | tr -d '\r\n[:space:]' || echo "unknown"
}
read_pstates() {
    local states=()
    for file in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do
        [[ -f "$file" ]] && states+=("$(<"$file")")
    done
    echo "${states[@]}"
}

cpu_cores=$(nproc)

# C-state structures
declare -A cstate_names
declare -A prev_cstate_times
cstate_columns=()

# Function to trim trailing newline and spaces from strings (state names)
read_and_trim_name() {
    tr -d '\r\n' < "$1" | xargs
}

for (( cpu=0; cpu<cpu_cores; cpu++ )); do
    enabled_list=()
    for state_dir in /sys/devices/system/cpu/cpu${cpu}/cpuidle/state*; do
        [[ -f "$state_dir/disable" && -f "$state_dir/name" && -f "$state_dir/time" ]] || continue
        if [[ "$(cat "$state_dir/disable")" == "0" ]]; then
            name=$(read_and_trim_name "$state_dir/name")
            key="${cpu}_${name}"
            enabled_list+=("$name")
            prev_cstate_times[$key]=$(<"$state_dir/time")
            cstate_columns+=("CPU${cpu}_${name}")
        fi
    done
    cstate_names[$cpu]="${enabled_list[*]}"
done


# --- Header ---
header="Timestamp"
for name in "${rapl_names[@]}"; do
    header+=",$name (W)"
done
for (( cpu=0; cpu<cpu_cores; cpu++ )); do
    header+=",CPU${cpu}_Freq (MHz)"
done
header+=",Governor"
pstate_status=$(get_pstate_status)
pstate_values=($(read_pstates))
if [[ "$pstate_status" == "active" ]]; then
    for (( i=0; i<${#pstate_values[@]}; i++ )); do
        header+=",CPU${i}_P-State"
    done
else
    header+=",P-State"
fi

# C-State Enabled Columns (per core)
for (( cpu=0; cpu<cpu_cores; cpu++ )); do
    header+=",CPU${cpu}_Enabled_CStates"
done


for col in "${cstate_columns[@]}"; do
    header+=",$col (s)"
done

log_buffer=()
log_buffer+=("$header")

# Init RAPL energy
declare -a prev_energy
for domain in "${rapl_domains[@]}"; do
    read -r val < "$domain/energy_uj"
    prev_energy+=("$val")
done

start_time=$(date +%s.%N)

# --- Main Loop ---
while $running; do
    now=$(date +%s.%N)
    elapsed=$(awk "BEGIN {print $now - $start_time}")
    if (( $(awk "BEGIN {print ($run_duration > 0 && $elapsed >= $run_duration)}") )); then
        break
    fi

    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    line="$timestamp"

    # RAPL power
    for i in "${!rapl_domains[@]}"; do
        domain="${rapl_domains[$i]}"
        read -r curr < "$domain/energy_uj"
        prev=${prev_energy[$i]}
        delta=$(( curr >= prev ? curr - prev : (max_val - prev + curr) ))
        power=$(awk -v d="$delta" -v s="$sleep_interval" 'BEGIN { printf "%.3f", d / 1000000 / s }')
        line+=",$power"
        prev_energy[$i]=$curr
    done

    # Frequencies
    for (( cpu=0; cpu<cpu_cores; cpu++ )); do
        freq_file="/sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_cur_freq"
        if [[ -f "$freq_file" ]]; then
            freq_khz=$(<"$freq_file")
            freq_mhz=$(awk "BEGIN { printf \"%.1f\", $freq_khz / 1000 }")
            line+=",$freq_mhz"
        else
            line+=",N/A"
        fi
    done

    # Governor
    line+=",$(get_current_governor)"

    # P-States
    if [[ "$pstate_status" == "active" ]]; then
        pstate_values=($(read_pstates))
        for val in "${pstate_values[@]}"; do
            line+=",$val"
        done
    else
        line+=",$pstate_status"
    fi

    # Enabled C-states per core
    for (( cpu=0; cpu<cpu_cores; cpu++ )); do
        enabled_states="${cstate_names[$cpu]}"
        line+=",$enabled_states"
    done


    # C-State delta values
    declare -A delta_cstate_values
    for (( cpu=0; cpu<cpu_cores; cpu++ )); do
        for name in ${cstate_names[$cpu]}; do
            for d in /sys/devices/system/cpu/cpu${cpu}/cpuidle/state*; do
                [[ -f "$d/name" ]] || continue
                [[ "$(read_and_trim_name "$d/name")" == "$name" ]] || continue
                curr_time=$(<"$d/time")
                key="CPU${cpu}_${name}"
                prev_time=${prev_cstate_times[$key]:-0}
                delta_us=$(( curr_time - prev_time ))
                delta_s=$(awk "BEGIN { printf \"%.3f\", $delta_us / 1000000 }")
                delta_cstate_values[$key]=$delta_s
                prev_cstate_times[$key]=$curr_time
                break
            done
        done
    done

    for col in "${cstate_columns[@]}"; do
        line+=","${delta_cstate_values[$col]:-0.000}
    done

    log_buffer+=("$line")
    sleep "$sleep_interval"
done

# Output to file
printf "%s\n" "${log_buffer[@]}" > "$output_file"
echo "Measurement complete. Data saved in $output_file"
