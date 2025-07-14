import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("training_dataset.csv")

# Define your custom order for C-states
cstate_order = ['POLL', 'C1', 'C1E', 'C3', 'C6', 'C7s', 'C8', 'C9', 'C10']

# Convert enabled_cstates column to categorical with the specified order
df['enabled_cstates'] = pd.Categorical(df['enabled_cstates'], categories=cstate_order, ordered=True)

# Style
sns.set(style="whitegrid")

# Filter only ACTIVE mode where p-state prefs exist
active_df = df[df['mode'] == 'ACTIVE'].copy()
active_df = active_df[active_df['pstate_pref'].notna() & (active_df['pstate_pref'] != "")]

# Make sure categorical ordering applies here too
active_df['enabled_cstates'] = pd.Categorical(active_df['enabled_cstates'], categories=cstate_order, ordered=True)


# --- 1. Power vs C-State (Grouped by Governor) ---
plt.figure(figsize=(14, 6))
sns.barplot(data=df, x="enabled_cstates", y="mean_power_pkg_w", hue="governor", errorbar=None)
plt.title("Power Consumption vs C-State (Grouped by Governor)")
plt.xlabel("Enabled C-State")
plt.ylabel("Mean Power (W)")
plt.xticks(rotation=45)
plt.legend(title="Governor")
plt.tight_layout()
plt.show()

# --- 3. Power vs C-State (Grouped by P-State Preference) ---
plt.figure(figsize=(14, 6))
sns.barplot(data=active_df, x="enabled_cstates", y="mean_power_pkg_w", hue="pstate_pref", errorbar=None)
plt.title("Power Consumption vs C-State (Grouped by P-State Preference)")
plt.xlabel("Enabled C-State")
plt.ylabel("Mean Power (W)")
plt.xticks(rotation=45)
plt.legend(title="P-State Pref")
plt.tight_layout()
plt.show()

# --- 2. Latency vs C-State (Grouped by Governor) ---
plt.figure(figsize=(14, 6))
sns.lineplot(data=df, x="enabled_cstates", y="mean_latency_ms", hue="governor", marker="o", errorbar=None)
plt.title("Benchmark Latency vs C-State (Grouped by Governor)")
plt.xlabel("Enabled C-State")
plt.ylabel("Mean Latency (ms)")
plt.xticks(rotation=45)
plt.legend(title="Governor")
plt.tight_layout()
plt.show()

# # --- 2. Without overlap ---
# g = sns.FacetGrid(df, col="governor", col_wrap=3, height=4, sharey=True)
# g.map_dataframe(sns.lineplot, x="enabled_cstates", y="mean_latency_ms", marker="o")
# g.set_titles(col_template="{col_name} Governor")
# g.set_axis_labels("Enabled C-State", "Mean Latency (ms)")
# for ax in g.axes.flat:
#     ax.tick_params(axis='x', rotation=45)
# plt.tight_layout()
# plt.show()

# --- 4. Latency vs C-State (Grouped by P-State Preference) ---
plt.figure(figsize=(14, 6))
sns.lineplot(data=active_df, x="enabled_cstates", y="mean_latency_ms", hue="pstate_pref", marker="o", errorbar=None)
plt.title("Benchmark Latency vs C-State (Grouped by P-State Preference)")
plt.xlabel("Enabled C-State")
plt.ylabel("Mean Latency (ms)")
plt.xticks(rotation=45)
plt.legend(title="P-State Pref")
plt.tight_layout()
plt.show()

# --- 5. CPU Utilization vs C-State (Grouped by Governor) ---
plt.figure(figsize=(14, 6))
sns.lineplot(data=df, x="enabled_cstates", y="mean_util", hue="governor", marker="o", errorbar=None)
plt.title("CPU Utilization vs C-State (Grouped by Governor)")
plt.xlabel("Enabled C-State")
plt.ylabel("CPU Utilization (%)")
plt.xticks(rotation=45)
plt.legend(title="Governor")
plt.tight_layout()
plt.show()

# --- 6. CPU Utilization vs C-State (Grouped by P-State Preference) ---
plt.figure(figsize=(14, 6))
sns.lineplot(data=active_df, x="enabled_cstates", y="mean_util", hue="pstate_pref", marker="o", errorbar=None)
plt.title("CPU Utilization vs C-State (Grouped by P-State Preference)")
plt.xlabel("Enabled C-State")
plt.ylabel("CPU Utilization (%)")
plt.xticks(rotation=45)
plt.legend(title="P-State Pref")
plt.tight_layout()
plt.show()


# --- 7.  CPU Frequency vs C-State (Grouped by Governor) ---
plt.figure(figsize=(14, 6))
sns.lineplot(data=df, x="enabled_cstates", y="mean_freq_mhz", hue="governor", marker="o", errorbar=None)
plt.title("CPU Frequency (MHz) vs C-State (Grouped by Governor)")
plt.xlabel("Enabled C-State")
plt.ylabel("CPU Frequency (MHz)")
plt.xticks(rotation=45)
plt.legend(title="Governor")
plt.tight_layout()
plt.show()

# --- 6. CPU Frequency vs C-State (Grouped by P-State Preference) ---
plt.figure(figsize=(14, 6))
sns.lineplot(data=active_df, x="enabled_cstates", y="mean_freq_mhz", hue="pstate_pref", marker="o", errorbar=None)
plt.title("CPU Frequency (MHz) vs C-State (Grouped by P-State Preference)")
plt.xlabel("Enabled C-State")
plt.ylabel("CPU Frequency (MHz)")
plt.xticks(rotation=45)
plt.legend(title="P-State Pref")
plt.tight_layout()
plt.show()