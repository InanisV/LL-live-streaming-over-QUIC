import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define the directory where the CSV files are stored
data_directory = "./"

# List of CSV filenames
confirmed_filenames = [
    "http2-BolaRule.csv", "http2-L2aRule.csv", "http2-LOLPRule.csv", "http2-ThroughputRule.csv",
    "quicgo-BolaRule.csv", "quicgo-L2aRule.csv", "quicgo-LOLPRule.csv", "quicgo-ThroughputRule.csv",
    "aioquic-BolaRule.csv", "aioquic-L2aRule.csv", "aioquic-LOLPRule.csv", "aioquic-ThroughputRule.csv",
    "quiche-BolaRule.csv", "quiche-L2aRule.csv", "quiche-LOLPRule.csv", "quiche-ThroughputRule.csv"
]

# Function to count the number of stalls based on the Buffer values
def count_stalls(file_path):
    data = pd.read_csv(file_path)
    # Calculate the points where Buffer goes from >0.1 to <0.1
    # Since the dash.js player start to stuck when Buffer belows 0.1
    is_stalled = (data['Buffer'] > 0.1).astype(int).diff() == -1
    return is_stalled.sum()

# Initialize a dictionary to store the stall counts for each file
stall_counts = {}

# Calculate the stall counts for each CSV file
for filename in confirmed_filenames:
    path = os.path.join(data_directory, filename)
    stall_counts[filename] = count_stalls(path)

# Define the protocols and algorithms for plotting
protocols_order_corrected = ['http2', 'quicgo', 'aioquic', 'quiche']
algorithms_order = ['BolaRule', 'L2aRule', 'LOLPRule', 'ThroughputRule']

# Prepare data for plotting stall counts
grouped_data_stalls = {protocol: {algorithm: 0 for algorithm in algorithms_order} for protocol in protocols_order_corrected}
for filename, stall_count in stall_counts.items():
    protocol, algorithm = filename.split('-')[0], filename.split('-')[1].replace('.csv', '')
    grouped_data_stalls[protocol][algorithm] = stall_count

# Plotting
fig, ax = plt.subplots(figsize=(22, 9))
bar_width = 0.12
indices = np.arange(len(protocols_order_corrected))

# Create bars for each algorithm within each protocol group
for i, algorithm in enumerate(algorithms_order):
    stall_values = [grouped_data_stalls[protocol][algorithm] for protocol in protocols_order_corrected]
    ax.bar(indices + i * bar_width, stall_values, width=bar_width, label=algorithm)

# Set chart labels and title
# ax.set_xlabel('Protocol')
ax.set_ylabel('Number of Stalls', fontsize=28)
# ax.set_title('Number of Stalls by Protocol and Algorithm')
ax.set_xticks(indices + bar_width / 2 * (len(algorithms_order) - 1))
ax.set_xticklabels(['HTTP/2', 'quic-go', 'aioquic', 'QUICHE'], fontsize=28)
ax.legend(fontsize=28)

# Customize y-axis range and tick labels
ax.set_ylim(0, 160)
ax.set_yticks(np.linspace(0, 160, 7))  # Creates 7 evenly spaced ticks from 0 to 1200
ax.set_yticklabels(np.linspace(0, 160, 7).astype(int), fontsize=24)  # Converts ticks to integer for display

# Customize appearance
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True)  # Only show horizontal grid lines
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('./stall_counts_chart_for_paper.png', format='png')
plt.show()
