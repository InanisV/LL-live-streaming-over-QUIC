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

# Function to calculate the average of SecondsBehindLive
def calculate_average_seconds_behind(file_path):
    data = pd.read_csv(file_path)
    return data[' SecondsBehindLive'].mean()

# Initialize a dictionary to store the average SecondsBehindLive for each file
average_seconds_behind = {}

# Calculate the average for each CSV file
for filename in confirmed_filenames:
    path = os.path.join(data_directory, filename)
    average_seconds_behind[filename] = calculate_average_seconds_behind(path)

# Define the protocols and algorithms for plotting
protocols_order_corrected = ['http2', 'quicgo', 'aioquic']
algorithms_order = ['BolaRule', 'L2aRule', 'LOLPRule', 'ThroughputRule']

# Prepare data for plotting
grouped_data_seconds_behind = {protocol: {algorithm: 0 for algorithm in algorithms_order} for protocol in protocols_order_corrected}
for filename, average in average_seconds_behind.items():
    protocol, algorithm = filename.split('-')[0], filename.split('-')[1].replace('_clean.csv', '')
    grouped_data_seconds_behind[protocol][algorithm] = average

# Plotting
fig, ax = plt.subplots(figsize=(22, 9))
bar_width = 0.12
indices = np.arange(len(protocols_order_corrected))

# Create bars for each algorithm within each protocol group
for i, algorithm in enumerate(algorithms_order):
    averages = [grouped_data_seconds_behind[protocol][algorithm] for protocol in protocols_order_corrected]
    ax.bar(indices + i * bar_width, averages, width=bar_width, label=algorithm)

# Set chart labels and title
# ax.set_xlabel('Protocol')
ax.set_ylabel('Average latency(s)', fontsize=28)
# ax.set_title('Average latency by Protocol and Algorithm')
ax.set_xticks(indices + bar_width / 2 * (len(algorithms_order) - 1))
ax.set_xticklabels(['HTTP/2', 'quic-go', 'aioquic'], fontsize=28)
ax.legend(fontsize=28)

# Customize y-axis range and tick labels
ax.set_ylim(0, 12)
ax.set_yticks(np.linspace(0, 12, 7))  # Creates 7 evenly spaced ticks from 0 to 1200
ax.set_yticklabels(np.linspace(0, 12, 7).astype(int), fontsize=24)  # Converts ticks to integer for display

# Remove top and right borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True)  # Only show horizontal grid lines
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('./average_latency_for_paper.png', format='png')
plt.show()
