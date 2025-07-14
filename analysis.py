####### This code create a csv file from all dataset with most relevant information #########


import re
import pandas as pd
from pathlib import Path

INPUT_DIR = Path(r'C:\Users\milad\Desktop\test1_csv')
OUTPUT_FILE = "training_dataset_idle.csv"

def parse_filename(filename):
    stem = filename.stem
    parts = stem.split('_')

    mode = parts[0] if len(parts) > 0 else ""
    governor = parts[1] if len(parts) > 1 else ""

    if mode == "ACTIVE":
        if len(parts) >= 4:
            pstate_pref = "_".join(parts[2:-1])
            enabled_cstates = parts[-1]
        else:
            pstate_pref = ""
            enabled_cstates = ""
    elif mode == "PASSIVE":
        pstate_pref = ""
        enabled_cstates = "_".join(parts[2:]) if len(parts) > 2 else ""
    else:
        pstate_pref = ""
        enabled_cstates = ""

    enabled_cstates = enabled_cstates.replace('_', '+')  # handle joined C-states
    return mode, governor, pstate_pref, enabled_cstates


def aggregate_metrics(df):
    # Compute mean metrics from the detailed CSV columns
    # Adapt column names as needed for your CSVs
    mean_power = df['package-0 (W)'].mean()
    mean_freq = df[[col for col in df.columns if 'Freq' in col]].mean(axis=1).mean()
    mean_util = df[[col for col in df.columns if 'Utilization' in col]].mean(axis=1).mean()
    mean_latency = df['Benchmark_Latency_ms'].mean()

    return mean_power, mean_freq, mean_util, mean_latency

def main():
    all_rows = []

    csv_files = list(INPUT_DIR.glob("*.csv"))
    print(f"Found {len(csv_files)} files.")

    for csv_file in csv_files:
        mode, governor, pstate_pref, enabled_cstates = parse_filename(csv_file)
        try:
            df = pd.read_csv(csv_file)

            mean_power, mean_freq, mean_util, mean_latency = aggregate_metrics(df)
            first_timestamp = df['Timestamp'].iloc[0] if 'Timestamp' in df.columns else None

            # ---- Sum C-state times per state across all cores ----
            cstate_sums = {}
            for col in df.columns:
                match = re.match(r'CPU\d+_(C\d+|C1E|C7s|POLL) \(ms\)', col)
                if match:
                    cstate = match.group(1)
                    cstate_sums[cstate] = cstate_sums.get(cstate, 0) + df[col].sum()

            row = {
                'first_timestamp': first_timestamp,
                'mode': mode,
                'governor': governor,
                'pstate_pref': pstate_pref.replace('_COMBO', ''),
                'enabled_cstates': enabled_cstates.replace('COMBO+', ''),
                'mean_power_pkg_w': mean_power,
                'mean_freq_mhz': mean_freq,
                'mean_util': mean_util,
                'mean_latency_ms': mean_latency
            }

            ordered_cstates = ['POLL', 'C1', 'C1E', 'C3', 'C6', 'C7s', 'C8', 'C9', 'C10']
            test_duration_ms = 59000  # 60 seconds in milliseconds
            num_cores = 8
            total_possible_time = test_duration_ms * num_cores

            for cstate in ordered_cstates:
                if cstate in cstate_sums:
                    row[f'percent_{cstate}'] = (cstate_sums[cstate] / total_possible_time) * 100
                else:
                    row[f'percent_{cstate}'] = 0.0

            # Compute percent of time in active mode
            total_cstate_percent = sum(row[f'percent_{c}'] for c in ordered_cstates)
            row['percent_active'] = max(0.0, 100.0 - total_cstate_percent)

            all_rows.append(row)


        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    # Create DataFrame and save
    result_df = pd.DataFrame(all_rows)

    # Sort by timestamp (ensure it's correctly interpreted as datetime or numeric)
    result_df = result_df.sort_values(by='first_timestamp')


    print("Saving combined training dataset to", OUTPUT_FILE)
    result_df.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()