#!/usr/bin/env python3

### This script has rapl power, p-states, c-states and time of enabled, and disabled ones, a benchmark tool and cpu utilization and frequency ###
import os
import re
import time
import signal
import argparse
from datetime import datetime
import numpy as np

sleep_interval = 0.5
output_file = "rapl_power_log.csv"
run_duration = 0  # seconds

running = True


def signal_handler(signum, frame):
    global running
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def detect_max_val(dir_path):
    file_path = os.path.join(dir_path, "max_energy_range_uj")
    if os.path.isfile(file_path):
        with open(file_path) as f:
            return int(f.read().strip())
    else:
        return 1 << 32  # fallback max 32-bit value


def read_and_trim_name(path):
    with open(path) as f:
        return f.read().strip()


def get_current_governor():
    path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return "unknown"


def get_pstate_status():
    path = "/sys/devices/system/cpu/intel_pstate/status"
    try:
        with open(path) as f:
            return f.read().strip().replace('\r', '').replace('\n', '')
    except Exception:
        return "unknown"


def read_pstates():
    values = []
    base_path = "/sys/devices/system/cpu"
    for entry in os.listdir(base_path):
        cpu_path = os.path.join(base_path, entry, "cpufreq", "energy_performance_preference")
        if os.path.isfile(cpu_path):
            try:
                with open(cpu_path) as f:
                    values.append(f.read().strip())
            except Exception:
                values.append("N/A")
    return values


def get_cpu_cores():
    return os.cpu_count()


def read_cstates(cpu_cores):
    cstate_names = {}            # Enabled states per CPU (for display)
    prev_cstate_times = {}       # Times for all states
    cstate_columns = []          # Column keys for all states

    for cpu in range(cpu_cores):
        enabled_list = []
        cpuidle_path = f"/sys/devices/system/cpu/cpu{cpu}/cpuidle"
        if not os.path.isdir(cpuidle_path):
            continue
        for state_dir in os.listdir(cpuidle_path):
            state_path = os.path.join(cpuidle_path, state_dir)
            disable_file = os.path.join(state_path, "disable")
            name_file = os.path.join(state_path, "name")
            time_file = os.path.join(state_path, "time")

            if not (os.path.isfile(disable_file) and os.path.isfile(name_file) and os.path.isfile(time_file)):
                continue
            try:
                with open(disable_file) as f:
                    disabled = f.read().strip()
                name = read_and_trim_name(name_file)
                key = f"CPU{cpu}_{name}"
                with open(time_file) as f:
                    prev_cstate_times[key] = int(f.read().strip())
                cstate_columns.append(key)
                if disabled == "0":
                    enabled_list.append(name)
            except Exception:
                continue
        cstate_names[cpu] = enabled_list

    return cstate_names, prev_cstate_times, cstate_columns


def benchmark_matrix_multiplication(size=300):
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    start = time.monotonic()
    np.dot(a, b)
    end = time.monotonic()
    return (end - start) * 1000  # in milliseconds


def read_cpu_utilization(prev_times):
    cpu_utils = {}
    current_times = {}
    with open("/proc/stat") as f:
        for line in f:
            if not line.startswith("cpu") or line.startswith("cpu "):  # Skip aggregate "cpu "
                continue
            parts = line.strip().split()
            cpu_id = parts[0]
            values = list(map(int, parts[1:]))
            idle = values[3] + values[4]
            total = sum(values)

            if cpu_id in prev_times:
                prev_idle, prev_total = prev_times[cpu_id]
                delta_idle = idle - prev_idle
                delta_total = total - prev_total
                if delta_total > 0:
                    usage = 100.0 * (1 - delta_idle / delta_total)
                else:
                    usage = 0.0
                cpu_utils[cpu_id] = usage
            current_times[cpu_id] = (idle, total)
    return cpu_utils, current_times




def main():
    global run_duration, output_file

    parser = argparse.ArgumentParser(description="RAPL power logger")
    parser.add_argument("duration", nargs='?', type=int, default=0,
                        help="Duration to run in seconds (default: unlimited)")
    parser.add_argument("-o", "--output", default="rapl_power_log.csv", help="Output CSV file")
    parser.add_argument("--benchmark", action="store_true",
                        help="Print benchmark stats after logging")
    args = parser.parse_args()

    run_duration = args.duration
    output_file = args.output

    rapl_domains = []
    rapl_names = []
    pattern = re.compile(r"intel-rapl:[0-9]+")
    base_path = "/sys/class/powercap"

    for entry in os.listdir(base_path):
        if not pattern.match(entry):
            continue
        domain_path = os.path.join(base_path, entry)
        energy_file = os.path.join(domain_path, "energy_uj")
        if not os.path.isfile(energy_file):
            continue
        rapl_domains.append(domain_path)
        name_file = os.path.join(domain_path, "name")
        if os.path.isfile(name_file):
            name = read_and_trim_name(name_file)
            rapl_names.append(name if name else "unknown")
        else:
            rapl_names.append("unknown")

    if not rapl_domains:
        print("No RAPL domains found!")
        return 1

    max_val = detect_max_val(rapl_domains[0])
    cpu_cores = get_cpu_cores()

    prev_cpu_times = {}
    cpu_utils, prev_cpu_times = read_cpu_utilization(prev_cpu_times)

    cstate_names, prev_cstate_times, cstate_columns = read_cstates(cpu_cores)
    all_cstate_columns = set(cstate_columns)
    pstate_status = get_pstate_status()

    header = ["Timestamp"]
    for name in rapl_names:
        header.append(f"{name} (W)")
    for cpu in range(cpu_cores):
        header.append(f"CPU{cpu}_Freq (MHz)")
        header.append(f"CPU{cpu}_Utilization (%)")
    header.append("Governor")

    if pstate_status == "active":
        pstate_values = read_pstates()
        for i in range(len(pstate_values)):
            header.append(f"CPU{i}_P-State")
    else:
        header.append("P-State")

    for cpu in range(cpu_cores):
        enabled_states = ",".join(cstate_names.get(cpu, []))
        header.append(f"CPU{cpu}_Enabled_CStates")

    for col in sorted(all_cstate_columns):
        header.append(f"{col} (ms)")

    header.append("Benchmark_Latency_ms")


    prev_energy = []
    for domain in rapl_domains:
        with open(os.path.join(domain, "energy_uj")) as f:
            prev_energy.append(int(f.read().strip()))

    start_time = time.monotonic()  # Changed for better precision

    # === BENCHMARK VARIABLES ===
    iteration_times = []
    overrun_count = 0
    # ===========================

    buffer = []
    buffer_size = 50  # Adjust as needed
    iteration = 0

    with open(output_file, "w") as f:
        f.write(",".join(header) + "\n")
        f.flush()

        while running:
            iteration_start = time.monotonic()
            elapsed = iteration_start - start_time
            if run_duration > 0 and elapsed >= run_duration:
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            line = [timestamp]

            # Read RAPL
            for i, domain in enumerate(rapl_domains):
                with open(os.path.join(domain, "energy_uj")) as f_energy:
                    curr = int(f_energy.read().strip())
                prev = prev_energy[i]
                delta = curr - prev if curr >= prev else (max_val - prev + curr)
                power = delta / 1_000_000 / sleep_interval
                line.append(f"{power:.3f}")
                prev_energy[i] = curr

            # Read frequency and utilization together
            cpu_utils, prev_cpu_times = read_cpu_utilization(prev_cpu_times)

            for cpu in range(cpu_cores):
                # Frequency
                freq_file = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_cur_freq"
                try:
                    with open(freq_file) as f_freq:
                        freq_khz = int(f_freq.read().strip())
                    freq_mhz = freq_khz / 1000
                    line.append(f"{freq_mhz:.1f}")
                except Exception:
                    line.append("N/A")

                # Utilization
                usage = cpu_utils.get(f"cpu{cpu}", 0.0)
                line.append(f"{usage:.2f}")

            line.append(get_current_governor())

            if pstate_status == "active":
                pstate_values = read_pstates()
                line.extend(pstate_values)
            else:
                line.append(pstate_status)

            # Read C-states
            cstate_names, current_cstate_times, current_cstate_columns = read_cstates(cpu_cores)
            all_cstate_columns.update(current_cstate_columns)

            for cpu in range(cpu_cores):
                enabled_states = " ".join(cstate_names.get(cpu, []))
                line.append(enabled_states)

            delta_cstate_values = {}
            for cpu in range(cpu_cores):
                for name in cstate_names.get(cpu, []):
                    key = f"CPU{cpu}_{name}"
                    curr_time = current_cstate_times.get(key, 0)
                    prev_time = prev_cstate_times.get(key, 0)
                    delta_us = curr_time - prev_time
                    delta_s = delta_us / 1_000
                    delta_cstate_values[key] = delta_s
                    prev_cstate_times[key] = curr_time

            for col in sorted(all_cstate_columns):
                line.append(f"{delta_cstate_values.get(col, 0.0):.3f}")

            benchmark_latency = benchmark_matrix_multiplication()
            line.append(f"{benchmark_latency:.3f}")

            buffer.append(",".join(line))

            if len(buffer) >= buffer_size:
                f.write("\n".join(buffer) + "\n")
                f.flush()
                buffer.clear()

            iteration_end = time.monotonic()
            iteration_duration = iteration_end - iteration_start
            iteration_times.append(iteration_duration)

            next_sample_time = start_time + (iteration + 1) * sleep_interval
            sleep_time = next_sample_time - iteration_end

            if sleep_time < 0:
                overrun_count += 1
                sleep_time = 0

            if sleep_time > 0:
                time.sleep(sleep_time)

            iteration += 1

        # Final flush
        if buffer:
            f.write("\n".join(buffer) + "\n")
            f.flush()

    # === PRINT BENCHMARK RESULTS ===
    if args.benchmark:
        if iteration_times:
            avg_time = sum(iteration_times) / len(iteration_times)
            min_time = min(iteration_times)
            max_time = max(iteration_times)
            print(f"--- Benchmark summary ---")
            print(f"Total iterations: {len(iteration_times)}")
            print(f"Average iteration time: {avg_time:.3f} s")
            print(f"Min iteration time: {min_time:.3f} s")
            print(f"Max iteration time: {max_time:.3f} s")
            print(f"Number of overruns (iteration longer than interval): {overrun_count}")
        else:
            print("No iterations recorded.")

    print(f"Measurement complete. Data saved in {output_file}")


if __name__ == "__main__":
    main()
