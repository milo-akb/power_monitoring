import os
import csv

folder_path = r'C:\Users\milad\Desktop\benchmark_results2'  # change this to your folder path

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)

        # Read all rows first
        with open(file_path, 'r', newline='') as f:
            reader = list(csv.reader(f))

        # Check if the file has at least 3 rows
        if len(reader) >= 3:
            # Copy third row to second row
            reader[1] = reader[2]

            # Write back all rows
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(reader)

            print(f"Processed {filename}")
        else:
            print(f"Skipped {filename}, not enough rows")
