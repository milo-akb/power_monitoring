#!/bin/bash

# Check if the user provided a policy argument
if [ -z "$1" ]; then
  echo "Usage: $0 <policy>"
  echo "Available policies: default, performance, balance_performance, balance_power, power"
  exit 1
fi

# Set the policy argument
policy=$1

# Loop through all CPU cores and set the policy
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
  if [ -e $cpu/cpufreq/energy_performance_preference ]; then
    echo $policy | sudo tee $cpu/cpufreq/energy_performance_preference
  else
    echo "Path $cpu/cpufreq/energy_performance_preference does not exist."
  fi
done

echo "P-state policy set to $policy for all CPUs."
