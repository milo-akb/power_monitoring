#!/bin/bash

sleep_interval=0.5
output_file="rapl_power_log.csv"

# Optional runtime duration in seconds, default: 0 (infinite)
run_duration=0

# Check for optional first argument: run duration in seconds
if [[ $# -ge 1 ]]; then
    if [[ "$1" =~ ^[0-9]+$ ]]; then
        run_duration="$1"
    else
        echo "Usage: $0 [run_duration_seconds]"
        exit 1
    fi
fi

# Flag to control the infinite loop
running=true

# Function to handle signals like SIGINT (Ctrl+C)
cleanup() {
    echo ""
    echo "Received interrupt signal, stopping measurement..."
    running=false
}
trap cleanup SIGINT SIGTERM

# Detect max_val for energy counter bit size automatically
detect_max_val() {
    local dir="$1"
    local max_energy_file="$dir/max_energy_range_uj"
    local max_val=0

    if [[ -f "$max_energy_file" ]]; then
        local max_energy=$(cat "$max_energy_file" 2>/dev/null)
        if [[ "$max_energy" =~ ^[0-9]+$ ]]; then
            if (( max_energy > 4294967295 )); then
                max_val=$((1<<64))
            else
                max_val=$((1<<32))
            fi
        fi
    fi

    if [[ $max_val -eq 0 ]]; then
        max_val=$((1<<32))
    fi

    echo "$max_val"
}

# Find all relevant top-level RAPL domains with energy_uj file
rapl_domains=()
rapl_names=()
for dir in /sys/class/powercap/intel-rapl:*; do
    base=$(basename "$dir")
    if [[ "$base" =~ ^intel-rapl:[0-9]+$ ]]; then
        if [[ -f "$dir/energy_uj" ]]; then
            rapl_domains+=("$dir")
            name=$(cat "$dir/name" 2>/dev/null)
            rapl_names+=("$name")
        fi
    fi
done

if [[ ${#rapl_domains[@]} -eq 0 ]]; then
    echo "No top-level RAPL packages found!"
    exit 1
fi

max_val=$(detect_max_val "${rapl_domains[0]}")

echo "RAPL Power Measurement started"
echo "Measurement interval: $sleep_interval seconds"
echo "Detected RAPL packages:"
for name in "${rapl_names[@]}"; do
    echo " - $name"
done

if (( run_duration > 0 )); then
    echo "Run duration set to $run_duration seconds"
else
    echo "Run duration set to infinite (until interrupted)"
fi
echo ""

header="Timestamp"
for name in "${rapl_names[@]}"; do
    header+=",$name"
done
echo "$header" > "$output_file"

read_energy() {
    local file="$1"
    local val=$(cat "$file" 2>/dev/null)
    if [[ ! "$val" =~ ^[0-9]+$ ]]; then
        echo "0"
    else
        echo "$val"
    fi
}

declare -a prev_energy
for domain in "${rapl_domains[@]}"; do
    prev_energy+=( $(read_energy "$domain/energy_uj") )
done

start_time=$(date +%s.%N)

# Main loop, will exit cleanly on signal or after duration if set
while $running; do
    now=$(date +%s.%N)
    elapsed=$(echo "$now - $start_time" | bc)

    # Exit loop if run_duration is set and elapsed time exceeded
    if (( run_duration > 0 )) && (( $(echo "$elapsed >= $run_duration" | bc) )); then
        echo "Reached run duration limit of $run_duration seconds."
        break
    fi

    next_time=$(echo "$sleep_interval * ( ( $elapsed / $sleep_interval ) + 1 )" | bc)
    sleep_time=$(echo "$start_time + $next_time - $now" | bc)

    awk -v t="$sleep_time" 'BEGIN { if (t > 0) exit 0; else exit 1 }' && sleep "$sleep_time"

    timestamp=$(date +"%Y-%m-%d %H:%M:%S.%3N")

    line="$timestamp"
    declare -a powers
    for i in "${!rapl_domains[@]}"; do
        curr=$(read_energy "${rapl_domains[$i]}/energy_uj")
        prev=${prev_energy[$i]}
        if (( curr < prev )); then
            delta=$(( (max_val - prev) + curr ))
        else
            delta=$(( curr - prev ))
        fi
        power=$(echo "scale=6; $delta / 1000000 / $sleep_interval" | bc)
        powers[$i]=$power
        line+=",$power"
        prev_energy[$i]=$curr
    done

    clear
    echo "RAPL Power Measurement started"
    echo "Measurement interval: $sleep_interval seconds"
    echo ""
    echo "RAPL Package    | Power (W)"
    echo "----------------+-----------"
    for i in "${!rapl_names[@]}"; do
        printf "%-15s | %s\n" "${rapl_names[$i]}" "${powers[$i]}"
    done
    echo ""

    echo "$line" >> "$output_file"
done

echo "Measurement stopped. CSV log saved to $output_file"
