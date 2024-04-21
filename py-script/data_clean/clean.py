import os
import pandas as pd

# Function to process all CSV files in the specified directory
def process_csv_files(directory):
    # Find all CSV files in the directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    for file in csv_files:
        file_path = os.path.join(directory, file)
        try:
            # Load the CSV file
            data = pd.read_csv(file_path)
            # Update the 'Timestamp' column to start from 0.3 and increment by 0.3 for each row
            data['Timestamp'] = [round(0.3 + 0.3 * i, 3) for i in range(len(data))]
            # Round all floating point numbers to 3 decimal places
            float_cols = data.select_dtypes(include=['float']).columns
            data[float_cols] = data[float_cols].round(3)
            # Define the new file path with a '_clean' suffix
            new_file_path = file_path.replace('.csv', '_clean.csv')
            # Save the modified data
            data.to_csv(new_file_path, index=False)
        except Exception as e:
            print(f"Failed to process {file}: {e}")

    return "All files have been processed and saved with the '_clean' suffix."

# Specify the directory where your CSV files are located
directory = './'
process_csv_files(directory)
