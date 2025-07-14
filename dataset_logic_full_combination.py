########### This code automates the logging process with the full combination of C-States ###########

import subprocess
import time
import os
from pathlib import Path
from itertools import combinations

# Constants and configurations
C_STATES = ['POLL', 'C1', 'C1E', 'C3', 'C6', 'C7s', 'C8', 'C9', 'C10']  # Adjust POLL included here per your system
P_STATES_ACTIVE_GOVERNOR_MODES = {
    'powersave': ['performance', 'balance_performance', 'balance_power', 'power'],
    'performance': ['performance'],  # fixed for performance governor
}
PASSIVE_GOVERNORS = ['conservative', 'ondemand', 'userspace', 'powersave', 'performance', 'schedutil']

OUTPUT_DIR = Path("benchmark_results")
OUTPUT_DIR.mkdir(exist_ok=True)

def run_cmd(cmd, check=True):
    print(f"Running command: {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def set_governor(governor):
    # Set governor for all CPUs
    cmd = f"echo {governor} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
    run_cmd(cmd)

def set_pstate_preference(pref):
    cmd = f"echo {pref} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference"
    run_cmd(cmd)

def set_pstate_status(status):
    # status: 'active' or 'passive'
    cmd = f"echo {status} | sudo tee /sys/devices/system/cpu/intel_pstate/status"
    run_cmd(cmd)

def disable_all_cstates():
    for disable_path in Path("/sys/devices/system/cpu").glob("cpu*/cpuidle/state*/disable"):
        try:
            with open(disable_path, 'w') as f:
                f.write('1')
        except PermissionError:
            print(f"Permission denied writing to {disable_path}")

def enable_cstate_only(target_cstate):
    disable_all_cstates()
    for cpuidle_dir in Path("/sys/devices/system/cpu").glob("cpu*/cpuidle"):
        for state_dir in cpuidle_dir.iterdir():
            name_file = state_dir / "name"
            disable_file = state_dir / "disable"
            if name_file.is_file() and disable_file.is_file():
                try:
                    with open(name_file) as f:
                        name = f.read().strip()
                    if name == target_cstate:
                        with open(disable_file, 'w') as f:
                            f.write('0')
                except PermissionError:
                    print(f"Permission denied accessing {disable_file} or {name_file}")

def enable_cstates_combo(cstate_combo):
    for cpuidle_dir in Path("/sys/devices/system/cpu").glob("cpu*/cpuidle"):
        for state_dir in cpuidle_dir.iterdir():
            name_file = state_dir / "name"
            disable_file = state_dir / "disable"
            if name_file.is_file() and disable_file.is_file():
                try:
                    with open(name_file) as f:
                        name = f.read().strip()
                    with open(disable_file, 'w') as f:
                        f.write('0' if name in cstate_combo else '1')
                except PermissionError:
                    print(f"Permission denied accessing {disable_file} or {name_file}")

def run_benchmark_and_logger(filename, duration=30):
    cmd = f"python3 rapl_logger2.py {duration} -o {filename} --benchmark"
    run_cmd(cmd)

def run_cstate_combinations(mode, governor, pstate_pref=None):
    for r in range(2, len(C_STATES) + 1):
        for combo in combinations(C_STATES, r):
            combo_str = "+".join(combo)
            print(f"Running {mode}: Governor={governor}, P-state={pstate_pref}, C-states={combo_str}")
            enable_cstates_combo(combo)
            fname_parts = [mode, governor]
            if pstate_pref:
                fname_parts.append(pstate_pref)
            fname_parts.append(f"COMBO_{combo_str}")
            fname = OUTPUT_DIR / ("_".join(fname_parts) + ".csv")
            run_benchmark_and_logger(fname)
            time.sleep(2)

def main():
    # ACTIVE P-STATES
    print("Setting P-states to ACTIVE mode")
    set_pstate_status('active')

    for governor, p_prefs in P_STATES_ACTIVE_GOVERNOR_MODES.items():
        set_governor(governor)
        for pstate_pref in p_prefs:
            set_pstate_preference(pstate_pref)
            for cstate in C_STATES:
                print(f"Running ACTIVE: Governor={governor}, P-state={pstate_pref}, C-state={cstate}")
                enable_cstate_only(cstate)
                fname = OUTPUT_DIR / f"ACTIVE_{governor}_{pstate_pref}_{cstate}.csv"
                run_benchmark_and_logger(fname)
                time.sleep(2)
            run_cstate_combinations("ACTIVE", governor, pstate_pref)

    # PASSIVE P-STATES
    print("Setting P-states to PASSIVE mode")
    set_pstate_status('passive')

    for governor in PASSIVE_GOVERNORS:
        set_governor(governor)
        for cstate in C_STATES:
            print(f"Running PASSIVE: Governor={governor}, C-state={cstate}")
            enable_cstate_only(cstate)
            fname = OUTPUT_DIR / f"PASSIVE_{governor}_{cstate}.csv"
            run_benchmark_and_logger(fname)
            time.sleep(2)
        run_cstate_combinations("PASSIVE", governor)

if __name__ == "__main__":
    main()
