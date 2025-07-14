import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns

rcParams['font.family'] = 'times new roman'

df_idle = pd.read_csv("training_dataset_idle.csv")
df_medium = pd.read_csv("training_dataset_medium.csv")
df_high = pd.read_csv("training_dataset_high.csv")

df_passive_idle = df_idle[df_idle['mode'] == 'PASSIVE']
df_passive_medium = df_medium[df_medium['mode'] == 'PASSIVE']
df_passive_high = df_high[df_high['mode'] == 'PASSIVE']

df_active_idle = df_idle[
    (df_idle['mode'] == 'ACTIVE') &
    (df_idle['governor'].isin(['powersave', 'performance']))
].copy()

# Disambiguate 'performance' pstate for each governor
df_active_idle['pstate_label'] = df_active_idle.apply(
    lambda row: f"{row['pstate_pref']} ({row['governor']})"
    if row['pstate_pref'] == 'performance' else row['pstate_pref'], axis=1
)

df_active_medium = df_medium[
    (df_medium['mode'] == 'ACTIVE') &
    (df_medium['governor'].isin(['powersave', 'performance']))
].copy()

# Disambiguate 'performance' pstate for each governor
df_active_medium['pstate_label'] = df_active_medium.apply(
    lambda row: f"{row['pstate_pref']} ({row['governor']})"
    if row['pstate_pref'] == 'performance' else row['pstate_pref'], axis=1
)

df_active_high = df_high[
    (df_high['mode'] == 'ACTIVE') &
    (df_high['governor'].isin(['powersave', 'performance']))
].copy()

# Disambiguate 'performance' pstate for each governor
df_active_high['pstate_label'] = df_active_high.apply(
    lambda row: f"{row['pstate_pref']} ({row['governor']})"
    if row['pstate_pref'] == 'performance' else row['pstate_pref'], axis=1
)



df_idle['num_cstates_enabled_idle'] = df_idle['enabled_cstates'].str.count(r'\+') + 1
summary_num_idle = df_idle.groupby('num_cstates_enabled_idle')['mean_power_pkg_w'].agg(['mean', 'min', 'max']).reset_index()


df_medium['num_cstates_enabled_medium'] = df_medium['enabled_cstates'].str.count(r'\+') + 1
summary_num_medium = df_medium.groupby('num_cstates_enabled_medium')['mean_power_pkg_w'].agg(['mean', 'min', 'max']).reset_index()


df_high['num_cstates_enabled_high'] = df_high['enabled_cstates'].str.count(r'\+') + 1
summary_num_high = df_high.groupby('num_cstates_enabled_high')['mean_power_pkg_w'].agg(['mean', 'min', 'max']).reset_index()


# Create the 2x3 subplot grid
fig, axes = plt.subplots(2, 3, figsize=(18, 10))  # Adjust figsize as needed


tab10_colors = [
    "#1f77b4",  # Blue
    "#ff7f0e",  # Orange
    "#2ca02c",  # Green
    "#d62728",  # Red
    "#9467bd",  # Purple
    "#8c564b",  # Brown
    "#e377c2",  # Pink
    "#7f7f7f",  # Gray
    "#bcbd22",  # Olive
    "#17becf"   # Cyan
]

governor_palette = {
    'performance': '#1f77b4',   # Blue
    'powersave': '#ff7f0e', # Orange
    'schedutil': '#e377c2', # Pink
    'ondemand': '#d62728',  # Red
    'conservative': '#8c564b',  # Brown
    'userspace': '#2ca02c'  # Green
}


pstate_palette = {
    'performance (powersave)': '#1f77b4',   # blue
    'balance_performance': '#ff7f0e',       # orange
    'power': '#2ca02c',                     # green
    'balance_power': '#d62728',             # red
    'performance (performance)': '#e377c2'  # pink
}


markers = {
    'performance': 'o',   # circle
    'powersave': 's',     # square
    'schedutil': '^',     # triangle up
    'ondemand': 'P',      # plus (filled)
    'conservative': 'X',  # X
    'userspace': 'D'      # diamond
}


# ===============================
# Plot 1: Latency vs Power, colored by pstate_pref
# ===============================
ax = axes[0, 0]  # First subplot in the first row
sns.scatterplot(
    data=df_active_idle,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='pstate_label',
    palette=pstate_palette,
    alpha=0.7,
    s=60,
    ax=ax
)
ax.set_title("A) Latency vs Power (P-State = Active, Idle load)", fontsize=16)
ax.set_xlabel("Mean Latency (ms)", fontsize=14)
ax.set_ylabel("Mean Power (W)", fontsize=14)
ax.set_xlim(10, 100)        # Fix X-axis range (latency)
ax.set_ylim(0, 60)       # Fix Y-axis range (power)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend_.remove()  # Hide legend



# ===============================
# Plot 2: Latency vs Power, colored by pstate_pref
# ===============================
ax = axes[0, 1]  # Second subplot in the first row
sns.scatterplot(
    data=df_active_medium,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='pstate_label',
    palette=pstate_palette,
    alpha=0.7,
    s=60,
    ax=ax
)
ax.set_title("B) Latency vs Power (P-State = Active, Medium load)", fontsize=16)
ax.set_xlabel("Mean Latency (ms)", fontsize=14)
ax.set_ylabel("")
ax.set_xlim(10, 100)        # Fix X-axis range (latency)
ax.set_ylim(0, 60)       # Fix Y-axis range (power)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend_.remove()  # Hide legend



# ===============================
# Plot 3: Latency vs Power, colored by pstate_pref
# ===============================
ax = axes[0, 2]  # Third subplot in the first row
sns.scatterplot(
    data=df_active_high,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='pstate_label',
    palette=pstate_palette,
    alpha=0.7,
    s=60,
    ax=ax
)
ax.set_title("C) Latency vs Power (P-State = Active, High load)", fontsize=16)
ax.set_xlabel("Mean Latency (ms)", fontsize=14)
ax.set_ylabel("")
ax.set_xlim(10, 100)        # Fix X-axis range (latency)
ax.set_ylim(0, 60)       # Fix Y-axis range (power)
ax.grid(True, linestyle='--', alpha=0.5)
# Move the legend inside bottom right (or adjust as needed)
ax.legend(
    title='P-State',
    loc='upper right',
    bbox_to_anchor=(1, 1),  # (x, y) inside axis coordinates
    frameon=True,
    framealpha=0.8,
    fontsize='x-large',
    title_fontsize='x-large'
)

# ------------------------------
# Subplot 4: Latency vs Power (PASSIVE idle)
# ------------------------------
ax = axes[1, 0]  # First subplot in the second row
sns.scatterplot(
    data=df_passive_idle,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='governor',
    palette=governor_palette,
    alpha=0.8,
    s=60,
    ax=ax
)
ax.set_title("D) Latency vs Power (P-State = Passive, Idle load)", fontsize=16)
ax.set_xlabel("Mean Latency (ms)", fontsize=14)
ax.set_ylabel("Mean Power (W)", fontsize=14)
ax.set_xlim(10, 100)        # Fix X-axis range (latency)
ax.set_ylim(0, 60)       # Fix Y-axis range (power)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend_.remove()  # Hide legend

# ------------------------------
# Subplot 5: Latency vs Power (PASSIVE medium)
# ------------------------------
ax = axes[1, 1]  # Second subplot in the second row
sns.scatterplot(
    data=df_passive_medium,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='governor',
    palette=governor_palette,
    alpha=0.8,
    s=60,
    ax=ax
)
ax.set_title("E) Latency vs Power (P-State = Passive, Medium load)", fontsize=16)
ax.set_xlabel("Mean Latency (ms)", fontsize=14)
ax.set_ylabel("")
ax.set_xlim(10, 100)        # Fix X-axis range (latency)
ax.set_ylim(0, 60)       # Fix Y-axis range (power)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend_.remove()  # Hide legend

# ------------------------------
# Subplot 6: Latency vs Power (PASSIVE high)
# ------------------------------
ax = axes[1, 2]  # Third subplot in the second row
sns.scatterplot(
    data=df_passive_high,
    markers=markers,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    hue='governor',
    palette=governor_palette,
    alpha=0.8,
    s=60,
    ax=ax
)
ax.set_title("F) Latency vs Power (P-State = Passive, High load)", fontsize=16)
ax.set_xlabel("Mean Latency (ms)", fontsize=14)
ax.set_ylabel("")
ax.set_xlim(10, 100)        # Fix X-axis range (latency)
ax.set_ylim(0, 60)       # Fix Y-axis range (power)
ax.grid(True, linestyle='--', alpha=0.4)

# Move the legend inside bottom right (or adjust as needed)
ax.legend(
    title='Governor',
    loc='upper right',
    bbox_to_anchor=(1, 1),  # (x, y) inside axis coordinates
    frameon=True,
    framealpha=0.8,
    fontsize='x-large',
    title_fontsize='x-large'
)

# Final layout and display
plt.tight_layout()
plt.show()



# Create 1 row and 3 columns of subplots
fig_cstate, axes_cstate = plt.subplots(1, 3, figsize=(18, 5))  # wider layout

# Shared Y-axis title only on the leftmost plot, so no clutter
y_label = "Mean Power (W)"
titles = ["Idle Load", "Medium Load", "High Load"]
title_numbers = ["A)", "B)", "C)"]
summaries = [
    (summary_num_idle, 'num_cstates_enabled_idle'),
    (summary_num_medium, 'num_cstates_enabled_medium'),
    (summary_num_high, 'num_cstates_enabled_high')
]
colors = ['teal', 'darkorange', 'slateblue']


for i, (summary_df, x_col) in enumerate(summaries):
    ax = axes_cstate[i]
    ax.errorbar(
        summary_df[x_col],
        summary_df['mean'],
        yerr=[
            summary_df['mean'] - summary_df['min'],
            summary_df['max'] - summary_df['mean']
        ],
        fmt='o-',
        capsize=7,
        color='#ff7f0e',  # line and marker edge color
        markerfacecolor='#ff7f0e',  # hollow marker
        markeredgecolor='#ff7f0e',  # marker border color
        ecolor='#1f77b4'  # error bar color
    )

    ax.set_title(f"{title_numbers[i]} Power vs C-states ({titles[i]})", fontsize=16)
    ax.set_xlabel("Number of Enabled C-states", fontsize=14)
    if i == 0:
        ax.set_ylabel(y_label, fontsize=14)
    else:
        ax.set_ylabel("")  # cleaner center/right plots
    ax.set_ylim(0, 60)
    ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()


# Assuming you already created this earlier:
fig3, axes3 = plt.subplots(2, 3, figsize=(18, 10))  # 2 rows, 3 columns
# Use the 6th subplot (second row, third column → index [1, 2])

ax = axes3[0, 0]
# Loop through each label and plot manually
for label, group in df_active_idle.groupby('pstate_label'):
    sns.kdeplot(
        data=group,
        x='mean_latency_ms',
        fill=True,
        common_norm=False,
        alpha=0.6,
        color=pstate_palette[label],
        label=label,
        ax=ax
    )

# Now the legend will work!
ax.set_title("Latency Density by P-state Pref (ACTIVE mode)", fontsize=14)
ax.set_xlabel("Mean Latency (ms)")
ax.set_ylabel("Density")
ax.grid(True, linestyle='--', alpha=0.5)


ax = axes3[0, 1]
# Loop through each label and plot manually
for label, group in df_active_medium.groupby('pstate_label'):
    sns.kdeplot(
        data=group,
        x='mean_latency_ms',
        fill=True,
        common_norm=False,
        alpha=0.6,
        color=pstate_palette[label],
        label=label,
        ax=ax
    )

# Now the legend will work!
ax.set_title("Latency Density by P-state Pref (ACTIVE mode)", fontsize=14)
ax.set_xlabel("Mean Latency (ms)")
ax.set_ylabel("Density")
ax.grid(True, linestyle='--', alpha=0.5)



ax = axes3[0, 2]
# Loop through each label and plot manually
for label, group in df_active_high.groupby('pstate_label'):
    sns.kdeplot(
        data=group,
        x='mean_latency_ms',
        fill=True,
        common_norm=False,
        alpha=0.6,
        color=pstate_palette[label],
        label=label,
        ax=ax
    )

# Now the legend will work!
ax.set_title("Latency Density by P-state Pref (ACTIVE mode)", fontsize=14)
ax.set_xlabel("Mean Latency (ms)")
ax.set_ylabel("Density")
ax.grid(True, linestyle='--', alpha=0.5)

ax.legend(
    title='P-States',
    loc='upper right',
    bbox_to_anchor=(1, 1),
    frameon=True,
    framealpha=0.8,
    fontsize='large',
    title_fontsize='large'
)



ax = axes3[1, 0]  # Choose the correct subplot (top-right)

# Define your custom governor color palette
governor_palette = {
    'performance': '#1f77b4',   # blue
    'powersave': '#ff7f0e',     # orange
    'schedutil': '#e377c2',     # pink
    'ondemand': '#d62728',      # red
    'conservative': '#8c564b',  # brown
    'userspace': '#2ca02c'      # green
}

# Filter only ACTIVE mode rows (or whatever filter you need)
df_governor_density = df_passive_idle.copy()  # You can use a broader df if needed

# Plot one KDE per governor
for gov, group in df_governor_density.groupby('governor'):
    sns.kdeplot(
        data=group,
        x='mean_latency_ms',
        fill=True,
        common_norm=False,
        alpha=0.6,
        color=governor_palette.get(gov, 'gray'),
        label=gov,
        ax=ax
    )

# Customize plot
ax.set_title("Latency Density by Governor (ACTIVE mode)", fontsize=14)
ax.set_xlabel("Mean Latency (ms)")
ax.set_ylabel("Density")
ax.grid(True, linestyle='--', alpha=0.5)



ax = axes3[1, 1]  # Choose the correct subplot (top-right)

# Define your custom governor color palette
governor_palette = {
    'performance': '#1f77b4',   # blue
    'powersave': '#ff7f0e',     # orange
    'schedutil': '#e377c2',     # pink
    'ondemand': '#d62728',      # red
    'conservative': '#8c564b',  # brown
    'userspace': '#2ca02c'      # green
}

# Filter only ACTIVE mode rows (or whatever filter you need)
df_governor_density = df_passive_medium.copy()  # You can use a broader df if needed

# Plot one KDE per governor
for gov, group in df_governor_density.groupby('governor'):
    sns.kdeplot(
        data=group,
        x='mean_latency_ms',
        fill=True,
        common_norm=False,
        alpha=0.6,
        color=governor_palette.get(gov, 'gray'),
        label=gov,
        ax=ax
    )

# Customize plot
ax.set_title("Latency Density by Governor (ACTIVE mode)", fontsize=14)
ax.set_xlabel("Mean Latency (ms)")
ax.set_ylabel("Density")
ax.grid(True, linestyle='--', alpha=0.5)



# --- Plot: Latency Density by Governor (ACTIVE mode) ---

ax = axes3[1, 2]  # Choose the correct subplot (top-right)

# Define your custom governor color palette
governor_palette = {
    'performance': '#1f77b4',   # blue
    'powersave': '#ff7f0e',     # orange
    'schedutil': '#e377c2',     # pink
    'ondemand': '#d62728',      # red
    'conservative': '#8c564b',  # brown
    'userspace': '#2ca02c'      # green
}

# Filter only ACTIVE mode rows (or whatever filter you need)
df_governor_density = df_passive_high.copy()  # You can use a broader df if needed

# Plot one KDE per governor
for gov, group in df_governor_density.groupby('governor'):
    sns.kdeplot(
        data=group,
        x='mean_latency_ms',
        fill=True,
        common_norm=False,
        alpha=0.6,
        color=governor_palette.get(gov, 'gray'),
        label=gov,
        ax=ax
    )

# Customize plot
ax.set_title("Latency Density by Governor (ACTIVE mode)", fontsize=14)
ax.set_xlabel("Mean Latency (ms)")
ax.set_ylabel("Density")
ax.grid(True, linestyle='--', alpha=0.5)

# Legend
ax.legend(
    title='Governor',
    loc='upper right',
    bbox_to_anchor=(1, 1),
    frameon=True,
    framealpha=0.8,
    fontsize='large',
    title_fontsize='large'
)

plt.tight_layout()
plt.show()