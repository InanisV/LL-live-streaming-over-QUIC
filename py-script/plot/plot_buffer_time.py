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

# Load and process each dataset
http2_data = load_and_process_data('http2-L2aRule_clean.csv')
quicgo_data = load_and_process_data('quicgo-L2aRule_clean.csv')
aioquic_data = load_and_process_data('aioquic-L2aRule_clean.csv')

# Apply smoothing to the buffer data
http2_buffer_smooth = smooth_data(http2_data['VideoBitrate'], 5)
quicgo_buffer_smooth = smooth_data(quicgo_data['VideoBitrate'], 5)
aioquic_buffer_smooth = smooth_data(aioquic_data['VideoBitrate'], 5)

# Create a single plot with a professional style suitable for publication
plt.figure(figsize=(12, 8))

# Plotting all three on the same graph, without markers and with professional style
plt.plot(http2_data['Timestamp'], http2_buffer_smooth, label='HTTP/2', color='navy', linewidth=2)
plt.plot(quicgo_data['Timestamp'], quicgo_buffer_smooth, label='quic-go', color='darkred', linewidth=2)
plt.plot(aioquic_data['Timestamp'], aioquic_buffer_smooth, label='aioquic', color='forestgreen', linewidth=2)

# Setting the title and labels with appropriate font sizes
plt.title('VideoBitrate vs. Time Comparison with L2aRule', fontsize=16)
plt.xlabel('Timestamp (s)', fontsize=14)
plt.ylabel('Buffer (s)', fontsize=14)

# Adding grid, legend, and adjusting the legend with a frame
plt.grid(True)
plt.legend(frameon=True, loc='upper right', fontsize=12)

# Show the plot
plt.show()
