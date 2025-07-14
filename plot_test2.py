import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv("training_dataset_high.csv")

# -------------------------------
# Normalize active and idle percentages
# -------------------------------
# Identify C-state percent columns (excluding active/idle)
cstate_cols = [col for col in df.columns if col.startswith("percent_") and col not in ["percent_active", "percent_idle"]]

# Recalculate total idle percentage as sum of all C-states
df['percent_idle'] = df[cstate_cols].sum(axis=1)

# Calculate total percent (active + idle)
df['total_percent'] = df['percent_idle'] + df['percent_active']

# Normalize values if total exceeds 100% (due to measurement/rounding errors)
mask = df['total_percent'] > 100.0
df.loc[mask, 'percent_idle'] = df.loc[mask, 'percent_idle'] / df.loc[mask, 'total_percent'] * 100
df.loc[mask, 'percent_active'] = df.loc[mask, 'percent_active'] / df.loc[mask, 'total_percent'] * 100

# Remove temporary total_percent column as normalization is done
df.drop(columns='total_percent', inplace=True)

# Clip values at 100% to handle floating point precision issues
df['percent_active'] = df['percent_active'].clip(upper=100)
df['percent_idle'] = df['percent_idle'].clip(upper=100)


df_passive = df[df['mode'] == 'PASSIVE']
summary_gov = df_passive.groupby('governor')[['percent_idle', 'percent_active']].mean().reset_index()

df_active_pwrsave = df[(df['mode'] == 'ACTIVE') & (df['governor'] == 'powersave')]
summary_pstate = df_active_pwrsave.groupby('pstate_pref')[['percent_idle', 'percent_active']].mean().reset_index()


# ===============================
# Plot 3️⃣: Scatter Plot for PASSIVE mode (Idle vs Active)
# ===============================
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_passive,
    x='percent_idle',
    y='percent_active',
    hue='governor',
    palette='tab10',
    alpha=0.7
)
# Optionally, plot a line showing x + y = 100% relationship:
# plt.plot([0, 100], [100, 0], linestyle='--', color='gray', label='x + y = 100')
plt.xlabel("Idle Time (%)")
plt.ylabel("Active Time (%)")
plt.title("Active vs Idle Time (PASSIVE mode)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ===============================
# Plot 4️⃣: Scatter Plot for ACTIVE mode + powersave (Idle vs Active)
# ===============================
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_active_pwrsave,
    x='percent_idle',
    y='percent_active',
    hue='pstate_pref',
    palette='tab10',
    alpha=0.7
)
# Optionally, plot line x + y = 100%
# plt.plot([0, 100], [100, 0], linestyle='--', color='gray', label='x + y = 100')
plt.xlabel("Idle Time (%)")
plt.ylabel("Active Time (%)")
plt.title("Active vs Idle Time (ACTIVE mode, governor = powersave)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ===============================
# Plot 5️⃣: Histogram - Distribution of Active & Idle Times
# ===============================
plt.figure(figsize=(10, 6))
plt.hist(df['percent_active'], bins=40, alpha=0.6, label='Active', color='orange')
plt.hist(df['percent_idle'], bins=40, alpha=0.6, label='Idle', color='skyblue')
plt.xlabel("Percentage of Time")
plt.ylabel("Number of Configurations")
plt.title("Distribution of Active and Idle Time Percentages")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ===============================
# Plot 6️⃣: Histogram Zoom - 0–4% and 96–100% ranges
# ===============================
# fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
#
# # Zoom into low range (0-4%)
# axes[0].hist(df['percent_active'], bins=40, range=(0, 4), alpha=0.6, label='Active', color='orange')
# axes[0].hist(df['percent_idle'], bins=40, range=(0, 4), alpha=0.6, label='Idle', color='skyblue')
# axes[0].set_title('Zoomed In: 0% to 4%')
# axes[0].set_xlabel('Percentage of Time')
# axes[0].set_ylabel('Number of Configurations')
# axes[0].legend()
# axes[0].grid(True)
#
# # Zoom into high range (96-100%)
# axes[1].hist(df['percent_active'], bins=40, range=(96, 100), alpha=0.6, label='Active', color='orange')
# axes[1].hist(df['percent_idle'], bins=40, range=(96, 100), alpha=0.6, label='Idle', color='skyblue')
# axes[1].set_title('Zoomed In: 96% to 100%')
# axes[1].set_xlabel('Percentage of Time')
# axes[1].legend()
# axes[1].grid(True)
#
# plt.tight_layout()
# plt.show()


# ===============================
# Plot 7️⃣: Latency vs Power (ACTIVE mode, governor=powersave), colored by pstate_pref
# ===============================
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_active_pwrsave,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='pstate_pref',
    palette='tab10',
    alpha=0.7,
    s=60
)
plt.title("Latency vs Power (ACTIVE mode, governor = powersave)", fontsize=13)
plt.xlabel("Mean Latency (ms)")
plt.ylabel("Mean Power (W)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='P-state Preference', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# ===============================
# Plot 8️⃣: Latency vs Power (PASSIVE mode), colored by governor
# ===============================
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_passive,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='governor',
    palette='Set2',
    alpha=0.7,
    s=60
)
plt.title("Latency vs Power (PASSIVE mode)", fontsize=13)
plt.xlabel("Mean Latency (ms)")
plt.ylabel("Mean Power (W)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='Governor', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# ===============================
# Plot 9️⃣: Subplots for Latency vs Power grouped by P-state Pref (ACTIVE mode)
# ===============================
pstate_groups = sorted(df_active_pwrsave['pstate_pref'].dropna().unique())
num_groups = len(pstate_groups)

fig, axes = plt.subplots(nrows=1, ncols=num_groups, figsize=(5*num_groups, 5), sharey=True)

for i, pstate in enumerate(pstate_groups):
    subset = df_active_pwrsave[df_active_pwrsave['pstate_pref'] == pstate]
    sns.scatterplot(
        data=subset,
        x='mean_latency_ms',
        y='mean_power_pkg_w',
        ax=axes[i],
        alpha=0.5,
        edgecolor='gray'
    )
    axes[i].set_title(f"P-state: {pstate}")
    axes[i].set_xlabel("Latency (ms)")
    if i == 0:
        axes[i].set_ylabel("Power (W)")
    else:
        axes[i].set_ylabel("")

plt.tight_layout()
plt.show()

# ===============================
# Plot 🔟: Subplots for Latency vs Power grouped by Governor (PASSIVE mode)
# ===============================
governor_groups = sorted(df_passive['governor'].dropna().unique())
num_groups = len(governor_groups)

fig, axes = plt.subplots(nrows=1, ncols=num_groups, figsize=(5*num_groups, 5), sharey=True)

for i, gov in enumerate(governor_groups):
    subset = df_passive[df_passive['governor'] == gov]
    sns.scatterplot(
        data=subset,
        x='mean_latency_ms',
        y='mean_power_pkg_w',
        ax=axes[i],
        alpha=0.5,
        edgecolor='gray'
    )
    axes[i].set_title(f"Governor: {gov}")
    axes[i].set_xlabel("Latency (ms)")
    if i == 0:
        axes[i].set_ylabel("Power (W)")
    else:
        axes[i].set_ylabel("")

plt.tight_layout()
plt.show()

# ===============================
# Plot 11️⃣: Pairplot for key numeric metrics
# ===============================
sns.pairplot(df[['mean_power_pkg_w', 'mean_freq_mhz', 'mean_latency_ms', 'mean_util', 'percent_idle']])
plt.suptitle("Pairwise Metric Comparison", y=1.02)
plt.show()

# ===============================
# Plot 12️⃣: KDE plots for Active vs Idle Times
# ===============================
sns.kdeplot(df['percent_active'], label="Active", fill=True, color='orange')
sns.kdeplot(df['percent_idle'], label="Idle", fill=True, color='skyblue')
plt.title("Density of Active vs Idle Times")
plt.legend()
plt.show()

# # ===============================
# # Plot 13️⃣: Zoomed KDE plots (0–5% and 95–100%)
# # ===============================
# fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
#
# # Zoom: 0–5%
# sns.kdeplot(df['percent_active'], fill=True, ax=axes[0], label="Active", color='tomato')
# sns.kdeplot(df['percent_idle'], fill=True, ax=axes[0], color='mediumseagreen')
# axes[0].set_xlim(0, 5)
# axes[0].set_title("Probability Density: 0% to 5%")
# axes[0].set_xlabel("Percentage")
# axes[0].set_ylabel("Density")
# axes[0].legend()
# axes[0].grid(True)
#
# # Zoom: 95–100%
# sns.kdeplot(df['percent_active'], fill=True, ax=axes[1], color='tomato')
# sns.kdeplot(df['percent_idle'], fill=True, ax=axes[1], label="Idle", color='mediumseagreen')
# axes[1].set_xlim(95, 100)
# axes[1].set_title("Probability Density: 95% to 100%")
# axes[1].set_xlabel("Percentage")
# axes[1].legend()
# axes[1].grid(True)
#
# plt.tight_layout()
# plt.show()


plt.figure(figsize=(10, 6))
sns.kdeplot(df['mean_power_pkg_w'], fill=True, color='purple', linewidth=2)
plt.title("Probability Density of Mean Power Consumption", fontsize=14)
plt.xlabel("Mean Power Consumption (W)")
plt.ylabel("Density")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


plt.figure(figsize=(10, 6))
sns.kdeplot(data=df[df['mode'] == 'ACTIVE'], x='mean_power_pkg_w', label='ACTIVE', fill=True, color='orange', alpha=0.5)
sns.kdeplot(data=df[df['mode'] == 'PASSIVE'], x='mean_power_pkg_w', label='PASSIVE', fill=True, color='skyblue', alpha=0.5)
plt.title("Power Consumption Density by Mode")
plt.xlabel("Mean Power Consumption (W)")
plt.ylabel("Density")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


plt.figure(figsize=(10, 6))
sns.kdeplot(data=df[df['mode'] == 'ACTIVE'], x='mean_latency_ms', label='ACTIVE', fill=True, color='orange', alpha=0.5)
sns.kdeplot(data=df[df['mode'] == 'PASSIVE'], x='mean_latency_ms', label='PASSIVE', fill=True, color='skyblue', alpha=0.5)
plt.title("Latency Density by Mode")
plt.xlabel("Mean Latency (ms)")
plt.ylabel("Density")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


df_active_pwrsave = df[(df['mode'] == 'ACTIVE') & (df['governor'] == 'powersave')]

plt.figure(figsize=(12, 6))
sns.kdeplot(
    data=df_active_pwrsave,
    x='mean_latency_ms',
    hue='pstate_pref',
    fill=True,
    common_norm=False,
    palette='tab10',
    alpha=0.6
)
plt.title("Latency Density by P-state Pref (ACTIVE mode, powersave governor)")
plt.xlabel("Mean Latency (ms)")
plt.ylabel("Density")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


# --- PASSIVE mode grouped by governor ---
df_passive = df[df['mode'] == 'PASSIVE']
summary_passive = df_passive.groupby('governor')['mean_power_pkg_w'].agg(['mean', 'min', 'max']).reset_index()

# Compute asymmetric errors
y = summary_passive['mean'].values
x = np.arange(len(summary_passive))
yerr_lower = summary_passive['mean'] - summary_passive['min']
yerr_upper = summary_passive['max'] - summary_passive['mean']
yerr = [yerr_lower.values, yerr_upper.values]

# Plot
plt.figure(figsize=(10, 6))
bars = plt.bar(x, y, yerr=yerr, capsize=5, color='skyblue', edgecolor='gray')
plt.xticks(x, summary_passive['governor'], rotation=45)
plt.ylabel("Mean Power (W)")
plt.title("Power Consumption by Governor (PASSIVE mode)")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


# Filter ACTIVE mode and relevant governors
df_active_selected = df[
    (df['mode'] == 'ACTIVE') &
    (df['governor'].isin(['powersave', 'performance']))
].copy()

# Label duplicate 'performance' pstate with governor to distinguish
df_active_selected['pstate_label'] = df_active_selected.apply(
    lambda row: f"{row['pstate_pref']} ({row['governor']})"
    if row['pstate_pref'] == 'performance' else row['pstate_pref'], axis=1
)

# Group by pstate_label (disambiguated)
summary_active = df_active_selected.groupby('pstate_label')['mean_power_pkg_w'].agg(['mean', 'min', 'max']).reset_index()

# Compute error bars
y = summary_active['mean'].values
x = np.arange(len(summary_active))
yerr_lower = summary_active['mean'] - summary_active['min']
yerr_upper = summary_active['max'] - summary_active['mean']
yerr = [yerr_lower.values, yerr_upper.values]

# Plot
plt.figure(figsize=(10, 6))
plt.bar(x, y, yerr=yerr, capsize=5, color='mediumpurple', edgecolor='gray')
plt.xticks(x, summary_active['pstate_label'], rotation=45)
plt.ylabel("Mean Power (W)")
plt.title("Power Consumption by P-state (ACTIVE mode: powersave + performance)")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


# ===============================
# Debugging info: max values check
# ===============================
print("Max percent active:", df['percent_active'].max())
print("Max percent idle:", df['percent_idle'].max())
print("Max combined active+idle:", (df['percent_active'] + df['percent_idle']).max())