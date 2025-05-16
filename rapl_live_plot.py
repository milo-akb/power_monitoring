import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import time
from datetime import datetime

csv_file = "rapl_power_log.csv"
refresh_interval = 0.5  # seconds

def read_data():
    try:
        df = pd.read_csv(csv_file, parse_dates=['Timestamp'])
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def live_plot():
    plt.ion()
    fig, ax = plt.subplots()

    while True:
        df = read_data()
        if df is not None and not df.empty:
            ax.clear()
            # Plot all power columns except Timestamp
            for col in df.columns[1:]:
                ax.plot(df['Timestamp'], df[col], label=col)

            ax.set_xlabel('Time')
            ax.set_ylabel('Power (W)')
            ax.set_title('Live RAPL Power Measurement')
            ax.legend()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.draw()
            plt.pause(refresh_interval)
        else:
            print("Waiting for data...")
            time.sleep(refresh_interval)

if __name__ == "__main__":
    live_plot()
