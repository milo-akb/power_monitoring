#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -d|-e state0 state1 ..."
    echo "  -d    Disable specified C-states"
    echo "  -e    Enable specified C-states"
    exit 1
}

# Check if at least two arguments are provided
if [ "$#" -lt 2 ]; then
    usage
fi

# Parse the flag
flag="$1"
shift

# Function to change C-state
change_cstate() {
    local action="$1"
    local state="$2"
    local value="$3"

    for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
        if [ -e "$cpu/cpuidle/$state/disable" ]; then
            echo "$value" | sudo tee "$cpu/cpuidle/$state/disable" > /dev/null
            echo "$action $state for $cpu"
        else
            echo "$state does not exist for $cpu"
        fi
    done
}

# Loop through the states and apply the action
case "$flag" in
    -d)
        for state in "$@"; do
            change_cstate "Disabling" "$state" 1
        done
        ;;
    -e)
        for state in "$@"; do
            change_cstate "Enabling" "$state" 0
        done
        ;;
    *)
        usage
        ;;
esac
