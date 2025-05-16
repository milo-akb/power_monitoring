#!/bin/bash

energy_before=()
energy_after=()
rapl_folders=()

read_energy() {
    local energy_file="$1"
    local energy_value=$(sudo cat "$energy_file" 2>/dev/null)
    echo "$energy_value"
}

# Collect top-level RAPL folders (intel-rapl:0, intel-rapl:1, etc., but not subdomains like intel-rapl:0:0)
for rapl_folder in /sys/class/powercap/intel-rapl:*; do
    if [[ "$rapl_folder" == *:* && "$rapl_folder" != *:*:* ]]; then
        rapl_folders+=("$rapl_folder")
    fi
done

# Read energy before sleep
for rapl_folder in "${rapl_folders[@]}"; do
    energy_before+=("$(read_energy "$rapl_folder/energy_uj")")
done

sleep 1

# Read energy after sleep
for rapl_folder in "${rapl_folders[@]}"; do
    energy_after+=("$(read_energy "$rapl_folder/energy_uj")")
done

calculate_power() {
    local energy_before="$1"
    local energy_after="$2"
    local delta=$((energy_after - energy_before))
    # Handle wrap-around (assume 32-bit counter max 2^32)
    if (( delta < 0 )); then
        delta=$(( (4294967296 - energy_before) + energy_after ))
    fi
    # Convert microjoules to joules and divide by 1 second to get watts
    echo "scale=6; $delta / 1000000" | bc
}

# Print power consumption per domain
for ((i=0; i < ${#rapl_folders[@]}; i++)); do
    rapl_name=$(basename "${rapl_folders[$i]}")
    rapl_name=${rapl_name/intel-rapl:/PhysicalGroup}
    power=$(calculate_power "${energy_before[$i]}" "${energy_after[$i]}")
    echo "$rapl_name: $power"
done
