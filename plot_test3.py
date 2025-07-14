import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv("training_dataset_high.csv")



sns.jointplot(
    data=df,
    x='mean_latency_ms',
    y='mean_power_pkg_w',
    kind='kde',  # or 'hex' for hexbin
    fill=True,
    cmap='coolwarm',
    height=8,
    space=0
)
plt.suptitle("Latency vs Power: Joint KDE", y=1.02)
plt.show()


sns.jointplot(
    data=df,
    x='mean_freq_mhz',
    y='mean_power_pkg_w',
    kind='kde',  # or 'hex' for hexbin
    fill=True,
    cmap='coolwarm',
    height=8,
    space=0
)
plt.suptitle("Latency vs Power: Joint KDE", y=1.02)
plt.show()


sns.jointplot(
    data=df,
    x='mean_util',
    y='mean_power_pkg_w',
    kind='kde',  # or 'hex' for hexbin
    fill=True,
    cmap='coolwarm',
    height=8,
    space=0
)
plt.suptitle("Latency vs Power: Joint KDE", y=1.02)
plt.show()
