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

# Function to calculate the average VideoBitrate within the first 300 seconds
def calculate_average_bitrate(file_path):
    data = pd.read_csv(file_path)
    # Filter data for the first 300 seconds
    filtered_data = data[data['Timestamp'] <= 300]
    return filtered_data['VideoBitrate'].mean()

# Initialize a dictionary to store the average VideoBitrate for each file within the first 300 seconds
average_bitrates = {}

# Calculate the average VideoBitrate for each CSV file
for filename in confirmed_filenames:
    path = os.path.join(data_directory, filename)
    average_bitrates[filename] = calculate_average_bitrate(path)

# Define the protocols and algorithms for plotting
protocols_order_corrected = ['http2', 'quicgo', 'aioquic', 'quiche']
algorithms_order = ['BolaRule', 'L2aRule', 'LOLPRule', 'ThroughputRule']

# Prepare data for plotting average bitrates
grouped_data_bitrates = {protocol: {algorithm: 0 for algorithm in algorithms_order} for protocol in protocols_order_corrected}
for filename, average_bitrate in average_bitrates.items():
    protocol, algorithm = filename.split('-')[0], filename.split('-')[1].replace('.csv', '')
    grouped_data_bitrates[protocol][algorithm] = average_bitrate

# Plotting the bar chart for average bitrates
fig, ax = plt.subplots(figsize=(22, 9))
bar_width = 0.12
indices = np.arange(len(protocols_order_corrected))

# Create bars for each algorithm within each protocol group
for i, algorithm in enumerate(algorithms_order):
    bitrate_values = [grouped_data_bitrates[protocol][algorithm] for protocol in protocols_order_corrected]
    ax.bar(indices + i * bar_width, bitrate_values, width=bar_width, label=algorithm)

# Set chart labels and title
# ax.set_xlabel('Protocol', fontsize=28)
ax.set_ylabel('Average Bitrate (bps)', fontsize=28)
# ax.set_title('Average Bitrate by Protocol and Algorithm within 0-300 Seconds')
ax.set_xticks(indices + bar_width / 2 * (len(algorithms_order) - 1))
ax.set_xticklabels(['HTTP/2', 'quic-go', 'aioquic', 'QUICHE'], fontsize=28)
# ax.set_yticklabels(ax.get_yticks(), fontsize=24)
ax.legend(fontsize=28)

# Customize y-axis range and tick labels
ax.set_ylim(0, 1200)
ax.set_yticks(np.linspace(0, 1200, 7))  # Creates 7 evenly spaced ticks from 0 to 1200
ax.set_yticklabels(np.linspace(0, 1200, 7).astype(int), fontsize=24)  # Converts ticks to integer for display

# Customize appearance
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True)  # Only show horizontal grid lines
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('./average_bitrate_chart_for_paper.png', format='png')
plt.show()
