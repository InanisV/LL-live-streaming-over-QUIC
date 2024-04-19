import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to smooth the data using a simple moving average
def smooth_data(y, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(y, window, 'same')

def load_and_process_data(file_path):
    # Load the CSV file
    data = pd.read_csv(file_path)
    # Strip any leading/trailing whitespace from column names
    data.columns = data.columns.str.strip()
    return data

ABR = 'ThroughputRule'

# Load and process each dataset
http2_data = load_and_process_data(f'http2-{ABR}_clean.csv')
quicgo_data = load_and_process_data(f'quicgo-{ABR}_clean.csv')
aioquic_data = load_and_process_data(f'aioquic-{ABR}_clean.csv')

# Remove the last 50 rows from each dataframe
http2_data = http2_data.iloc[:-140]
quicgo_data = quicgo_data.iloc[:-140]
aioquic_data = aioquic_data.iloc[:-140]

# Apply smoothing to the buffer data
http2_buffer_smooth = smooth_data(http2_data['Buffer'], 5)
quicgo_buffer_smooth = smooth_data(quicgo_data['Buffer'], 5)
aioquic_buffer_smooth = smooth_data(aioquic_data['Buffer'], 5)

# Create a single plot with a professional style suitable for publication
plt.figure(figsize=(16, 9))

# Plotting all three on the same graph, without markers and with professional style
plt.plot(http2_data['Timestamp'], http2_buffer_smooth, label='HTTP/2', color='navy', linewidth=2)
plt.plot(quicgo_data['Timestamp'], quicgo_buffer_smooth, label='quic-go', color='darkred', linewidth=2)
plt.plot(aioquic_data['Timestamp'], aioquic_buffer_smooth, label='aioquic', color='forestgreen', linewidth=2)

# Setting the title and labels with appropriate font sizes
# plt.title(f'Buffer vs. Time Comparison with {ABR}', fontsize=16)
plt.xlabel('Timestamp (s)', fontsize=28)
plt.ylabel('Buffer (s)', fontsize=28)

# Setting the font size of the tick labels on both axes
plt.xticks(fontsize=24)
plt.yticks(fontsize=24)

# Adding grid, legend, and adjusting the legend with a frame
plt.grid(True)
plt.legend(frameon=True, loc='upper right', fontsize=28)

# Show the plot
plt.tight_layout()
plt.savefig(f'./Buffer vs. Time Comparison with {ABR}.png', format='png')
plt.show()
