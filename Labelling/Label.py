import pandas as pd
import os
import re  # for extracting run_id from filename

# Mapping anomaly types
anomaly_map = {
    "Normal": 0,
    "Freeze": 1,
    "Step": 2,
    "Ramp": 3
}

# Relative paths (relative to project root)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_folder = os.path.join(base_dir, "Dataset")
output_folder = os.path.join(base_dir, "Labelled Data")

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

all_data = []  # to optionally combine later

for file in os.listdir(input_folder):
    if file.endswith(".csv"):
        file_path = os.path.join(input_folder, file)
        df = pd.read_csv(file_path)

        # Detect anomaly type from filename
        anomaly_type = None
        for key in anomaly_map.keys():
            if key.lower() in file.lower():
                anomaly_type = key
                break

        if anomaly_type is None:
            print(f"⚠️ Skipping {file}, no anomaly type found in filename")
            continue

        # Add / overwrite Anomaly column
        df["Anomaly"] = anomaly_map[anomaly_type]

        # Extract run_id from filename (first number found)
        match = re.search(r"(\d+)", file)
        run_id = match.group(1) if match else "NA"

        # New filename format
        new_filename = f"{anomaly_type}_{run_id}.csv"

        # Save updated file
        output_path = os.path.join(output_folder, new_filename)
        df.to_csv(output_path, index=False)

        # Add to combined dataset
        all_data.append(df)

        print(f"✅ Processed {file} → {new_filename}")

# Save merged dataset
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_path = os.path.join(output_folder, "Master_Labeled.csv")
    merged_df.to_csv(merged_path, index=False)
    print(f"\n📌 Combined dataset saved as: {merged_path}")

print("\n🎯 All CSVs processed successfully.")
