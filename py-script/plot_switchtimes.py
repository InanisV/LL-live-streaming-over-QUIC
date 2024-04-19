import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# File path for the datasets
data_directory = "./"

# Filenames for the datasets
confirmed_filenames = [
    "http2-BolaRule_clean.csv", "http2-L2aRule_clean.csv", "http2-LOLPRule_clean.csv", "http2-ThroughputRule_clean.csv",
    "quicgo-BolaRule_clean.csv", "quicgo-L2aRule_clean.csv", "quicgo-LOLPRule_clean.csv", "quicgo-ThroughputRule_clean.csv",
    "aioquic-BolaRule_clean.csv", "aioquic-L2aRule_clean.csv", "aioquic-LOLPRule_clean.csv", "aioquic-ThroughputRule_clean.csv"
]

# Function to count the switches in the VideoIndexDownloading column
def count_switches(file_path):
    data = pd.read_csv(file_path)
    return (data[' VideoIndexDownloading'].diff() != 0).sum()

# Initialize dictionary to hold switch counts for each file
switches_count = {}

# Process each file and count the switches
for filename in confirmed_filenames:
    path = os.path.join(data_directory, filename)
    switches_count[filename] = count_switches(path)

# Order of protocols and algorithms for plotting
protocols_order_corrected = ['http2', 'quicgo', 'aioquic']
algorithms_order = ['BolaRule', 'L2aRule', 'LOLPRule', 'ThroughputRule']

# Initialize dictionary to hold counts of switches for each algorithm for each protocol
grouped_data = {protocol: {algorithm: 0 for algorithm in algorithms_order} for protocol in protocols_order_corrected}

# Populate dictionary with switch counts
for filename, switch_count in switches_count.items():
    protocol, algorithm = filename.split('-')[0], filename.split('-')[1].replace('_clean.csv', '')
    grouped_data[protocol][algorithm] = switch_count

# Plot the grouped bar chart
fig, ax = plt.subplots(figsize=(22, 9))
bar_width = 0.12
indices = np.arange(len(protocols_order_corrected))

# Create bars for each algorithm within each protocol group
for i, algorithm in enumerate(algorithms_order):
    counts = [grouped_data[protocol][algorithm] for protocol in protocols_order_corrected]
    ax.bar(indices + i * bar_width, counts, width=bar_width, label=algorithm)

# Set the x-axis and y-axis labels, and chart title
# ax.set_xlabel('Protocol')
ax.set_ylabel('Number of Video Bitrate Switches', fontsize=28)
# ax.set_title('Switches by Protocol and Algorithm')
ax.set_xticks(indices + bar_width / 2 * (len(algorithms_order) - 1))
ax.set_xticklabels(['HTTP/2', 'quic-go', 'aioquic'], fontsize=28)

# Customize the plot to be more formal for paper
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True)  # Only show horizontal grid lines
ax.set_axisbelow(True)

# Customize the legend
ax.legend(fontsize=28)

# Customize y-axis range and tick labels
ax.set_ylim(0, 200)
ax.set_yticks(np.linspace(0, 200, 7))  # Creates 7 evenly spaced ticks from 0 to 1200
ax.set_yticklabels(np.linspace(0, 200, 7).astype(int), fontsize=24)  # Converts ticks to integer for display

# Save the plot to a file
plt.tight_layout()
plt.savefig('./switches_chart_for_paper.png', format='png')

plt.show()
