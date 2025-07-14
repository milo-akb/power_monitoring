####### Thic code prints the mean values from the training files #########


import pandas as pd

# Load the datasets
df_idle = pd.read_csv("training_dataset_idle.csv")
df_medium = pd.read_csv("training_dataset_medium.csv")
df_high = pd.read_csv("training_dataset_high.csv")

# Compute the average power values
avg_idle_power = df_idle['mean_power_pkg_w'].mean()
avg_medium_power = df_medium['mean_power_pkg_w'].mean()
avg_high_power = df_high['mean_power_pkg_w'].mean()

# Print the results
print(f"Average Idle Power:   {avg_idle_power:.3f} W")
print(f"Average Medium Power: {avg_medium_power:.3f} W")
print(f"Average High Power:   {avg_high_power:.3f} W")


# Compute the average frequency values
avg_idle_frequency = df_idle['mean_freq_mhz'].mean()
avg_medium_frequency = df_medium['mean_freq_mhz'].mean()
avg_high_frequency = df_high['mean_freq_mhz'].mean()

# Print the results
print(f"Average Idle Frequency:   {avg_idle_frequency:.3f} MHz")
print(f"Average Medium Frequency: {avg_medium_frequency:.3f} MHz")
print(f"Average High Frequency:   {avg_high_frequency:.3f} MHz")


# Compute the average utilization values
avg_idle_util = df_idle['mean_util'].mean()
avg_medium_util = df_medium['mean_util'].mean()
avg_high_util = df_high['mean_util'].mean()

# Print the results
print(f"Average Idle Utilization:   {avg_idle_util:.3f} %")
print(f"Average Medium Utilization: {avg_medium_util:.3f} %")
print(f"Average High Utilization:   {avg_high_util:.3f} %")



# Compute the average latency values
avg_idle_latency = df_idle['mean_latency_ms'].mean()
avg_medium_latency = df_medium['mean_latency_ms'].mean()
avg_high_latency = df_high['mean_latency_ms'].mean()

# Print the results
print(f"Average Idle Latency:   {avg_idle_latency:.3f} ms")
print(f"Average Medium Latency: {avg_medium_latency:.3f} ms")
print(f"Average High Latency:   {avg_high_latency:.3f} ms")


# Compute the average latency values
avg_percent_active_idle = df_idle['percent_active'].mean()
avg_percent_active_medium = df_medium['percent_active'].mean()
avg_percent_active_high = df_high['percent_active'].mean()

# Print the results
print(f"Average Idle Percent Active:   {avg_percent_active_idle:.3f} %")
print(f"Average Medium Percent Active: {avg_percent_active_medium:.3f} %")
print(f"Average High Percent Active:   {avg_percent_active_high:.3f} %")

# Print the results
print(f"Average Idle Percent Sleep:   {100 - avg_percent_active_idle:.3f} %")
print(f"Average Medium Percent Sleep: {100 - avg_percent_active_medium:.3f} %")
print(f"Average High Percent Sleep:   {100 - avg_percent_active_high:.3f} %")