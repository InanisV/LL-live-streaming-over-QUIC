import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define the directory where the CSV files are stored
data_directory = "./"

# List of CSV filenames
confirmed_filenames = [
    "http2-BolaRule_clean.csv", "http2-L2aRule_clean.csv", "http2-LOLPRule_clean.csv", "http2-ThroughputRule_clean.csv",
    "quicgo-BolaRule_clean.csv", "quicgo-L2aRule_clean.csv", "quicgo-LOLPRule_clean.csv", "quicgo-ThroughputRule_clean.csv",
    "aioquic-BolaRule_clean.csv", "aioquic-L2aRule_clean.csv", "aioquic-LOLPRule_clean.csv", "aioquic-ThroughputRule_clean.csv"
]

# Function to count the number of stalls based on the Buffer values
def count_stalls(file_path):
    data = pd.read_csv(file_path)
    # Calculate the points where Buffer goes from >0.1 to <0.1
    is_stalled = (data[' Buffer'] > 0.1).astype(int).diff() == -1
    return is_stalled.sum()

# Initialize a dictionary to store the stall counts for each file
stall_counts = {}

# Calculate the stall counts for each CSV file
for filename in confirmed_filenames:
    path = os.path.join(data_directory, filename)
    stall_counts[filename] = count_stalls(path)

# Define the protocols and algorithms for plotting
protocols_order_corrected = ['http2', 'quicgo', 'aioquic']
algorithms_order = ['BolaRule', 'L2aRule', 'LOLPRule', 'ThroughputRule']

# Prepare data for plotting stall counts
grouped_data_stalls = {protocol: {algorithm: 0 for algorithm in algorithms_order} for protocol in protocols_order_corrected}
for filename, stall_count in stall_counts.items():
    protocol, algorithm = filename.split('-')[0], filename.split('-')[1].replace('_clean.csv', '')
    grouped_data_stalls[protocol][algorithm] = stall_count

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
bar_width = 0.15
indices = np.arange(len(protocols_order_corrected))

# Create bars for each algorithm within each protocol group
for i, algorithm in enumerate(algorithms_order):
    stall_values = [grouped_data_stalls[protocol][algorithm] for protocol in protocols_order_corrected]
    ax.bar(indices + i * bar_width, stall_values, width=bar_width, label=algorithm)

# Set chart labels and title
ax.set_xlabel('Protocol')
ax.set_ylabel('Number of Stalls')
ax.set_title('Number of Stalls by Protocol and Algorithm')
ax.set_xticks(indices + bar_width / 2 * (len(algorithms_order) - 1))
ax.set_xticklabels(protocols_order_corrected)
ax.legend()

# Customize appearance
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True)  # Only show horizontal grid lines
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('./stall_counts_chart_for_paper.pdf', format='pdf')
plt.show()
