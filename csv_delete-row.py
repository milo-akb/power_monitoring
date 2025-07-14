import os
import csv

folder_path = r'C:\Users\milad\Desktop\test3_csv'  # update this path

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)

        # Read all rows
        with open(file_path, 'r', newline='') as f:
            reader = list(csv.reader(f))

        # Remove second row if exists
        if len(reader) >= 2:
            removed_row = reader.pop(1)  # remove second row (index 1)

            # Write back remaining rows
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(reader)

            print(f"Removed second row from {filename}")
        else:
            print(f"Skipped {filename}, not enough rows")
