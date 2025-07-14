import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv("training_dataset_high.csv")


# List of valid C-states
valid_cstates = ['POLL', 'C1', 'C1E', 'C3', 'C6', 'C7s', 'C8', 'C9', 'C10']

# Filter rows where exactly one C-state is enabled (i.e., no '+' present)
df_single_cstate = df[df['enabled_cstates'].isin(valid_cstates)].copy()


# Group by the single enabled C-state and compute statistics
summary_cstate = (
    df_single_cstate
    .groupby('enabled_cstates')['mean_power_pkg_w']
    .agg(['mean', 'min', 'max'])
    .reset_index()
)

# Prepare data for plotting
y = summary_cstate['mean'].values
x = np.arange(len(summary_cstate))
yerr_lower = summary_cstate['mean'] - summary_cstate['min']
yerr_upper = summary_cstate['max'] - summary_cstate['mean']
yerr = [yerr_lower.values, yerr_upper.values]

# Plot
plt.figure(figsize=(10, 6))
bars = plt.bar(x, y, yerr=yerr, capsize=5, color='mediumseagreen', edgecolor='gray')
plt.xticks(x, summary_cstate['enabled_cstates'], rotation=45)
plt.ylabel("Mean Power (W)")
plt.title("Power Consumption with Only One Enabled C-state")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


df['num_cstates_enabled'] = df['enabled_cstates'].str.count(r'\+') + 1

summary_num = df.groupby('num_cstates_enabled')['mean_power_pkg_w'].agg(['mean', 'min', 'max']).reset_index()

# Plot
plt.figure(figsize=(8,5))
plt.errorbar(
    summary_num['num_cstates_enabled'],
    summary_num['mean'],
    yerr=[summary_num['mean'] - summary_num['min'], summary_num['max'] - summary_num['mean']],
    fmt='o-', capsize=5, color='teal'
)
plt.title("Power vs Number of Enabled C-states")
plt.xlabel("Number of Enabled C-states")
plt.ylabel("Mean Power (W)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

#
# # --- Compute number of enabled C-states ---
# df['num_cstates'] = df['enabled_cstates'].str.count(r'\+') + 1
# print(df['mean_power_pkg_w'].min())
#
#
# plt.figure(figsize=(10, 6))
#
# for n in sorted(df['num_cstates'].unique()):
#     subset = df[df['num_cstates'] == n]
#     plt.hist(subset['mean_power_pkg_w'], bins=40, alpha=0.3, density=True, label=f"{n} C-states")
#
# plt.title("Power Distribution by Number of Enabled C-states")
# plt.xlabel("Mean Power (W)")
# plt.ylabel("Density")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#
#
# num_groups = sorted(df['num_cstates'].unique())
# fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 12), sharex=True, sharey=True)
# axes = axes.flatten()
#
# for i, n in enumerate(num_groups):
#     subset = df[df['num_cstates'] == n]
#     axes[i].hist(subset['mean_power_pkg_w'], bins=30, alpha=0.7, color='C'+str(i), density=True)
#     axes[i].set_title(f"{n} C-states")
#     axes[i].grid(True)
#
# plt.tight_layout()
# plt.show()
#
#
# plt.figure(figsize=(10, 6))
# for n in sorted(df['num_cstates'].unique()):
#     subset = df[df['num_cstates'] == n]
#     sns.kdeplot(
#         subset['mean_power_pkg_w'],
#         label=f"{n} C-states",
#         fill=False,
#         clip=(0, None),  # restrict to non-negative power
#         bw_adjust=0.2,   # less smooth
#         alpha=0.7
#     )
# plt.title("Power Distribution by Number of Enabled C-states")
# plt.xlabel("Mean Power (W)")
# plt.ylabel("Density")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#





