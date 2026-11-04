import csv
import json
import os
import shutil


# My Inputs
SEED_DIGIT = 8 

# Derived Rules
TARGET_OS = "Android" if SEED_DIGIT % 2 == 0 else "iOS"
TARGET_BEHAVIOR_CLASS = (SEED_DIGIT % 5) + 1

# File paths
INPUT_FILE = "user_behavior_dataset.csv"
OUTPUT_CSV = "filtered_user_behavior.csv"
OUTPUT_JSON = "device_profile_summary.json"
BACKUP_CSV = "filtered_user_behavior_backup.csv"

print(f"--- Running Exercise 2 Analysis ---")
print(f"Target OS: {TARGET_OS}")
print(f"Target Behavior Class: {TARGET_BEHAVIOR_CLASS}")

if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} not found. Please place it in the same directory.")
    exit()

total_dataset_records = 0
matching_os_count = 0
selected_records = []

total_battery_drain = 0.0
total_data_usage = 0.0

with open(INPUT_FILE, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        total_dataset_records += 1
        
        # Safe extraction and normalization
        current_os = row.get("Operating System", "").strip()
        behavior_class_str = row.get("User Behavior Class", "").strip()
        
        # 1. Match operating system
        if current_os.lower() == TARGET_OS.lower():
            matching_os_count += 1
            
            # 2. Match target behavior class
            if behavior_class_str.isdigit() and int(behavior_class_str) == TARGET_BEHAVIOR_CLASS:
                try:
                    battery = float(row.get("Battery Drain (mAh/day)", 0))
                    data_use = float(row.get("Data Usage (MB/day)", 0))
                except ValueError:
                    continue # Skip anomalies or row corruption safely
                
                total_battery_drain += battery
                total_data_usage += data_use
                
                # Keep fields requested for export
                selected_records.append({
                    "User ID": row.get("User ID", "").strip(),
                    "Device Model": row.get("Device Model", "").strip(),
                    "Operating System": current_os,
                    "Battery Drain (mAh/day)": battery,
                    "Data Usage (MB/day)": data_use
                })

# 3. Handle cases with no matching records avoiding division-by-zero
selected_count = len(selected_records)
if selected_count > 0:
    avg_battery = round(total_battery_drain / selected_count, 2)
    avg_data = round(total_data_usage / selected_count, 2)
else:
    avg_battery = 0.0
    avg_data = 0.0

# 4. Export selected users and fields to CSV
fields_to_export = ["User ID", "Device Model", "Operating System", "Battery Drain (mAh/day)", "Data Usage (MB/day)"]
with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fields_to_export)
    writer.writeheader()
    writer.writerows(selected_records)

# 5. Write JSON summary & count verification check
count_verification = "Passed" if selected_count == len(selected_records) else "Failed"

# 6. Create a backup of the exported CSV file and get its file size
shutil.copyfile(OUTPUT_CSV, BACKUP_CSV)
backup_size_bytes = os.path.getsize(BACKUP_CSV)

summary_data = {
    "Operating system and behavior class": f"{TARGET_OS} | Class {TARGET_BEHAVIOR_CLASS}",
    "Total records in dataset": total_dataset_records,
    "Records matching operating system": matching_os_count,
    "Records in target behavior class": selected_count,
    "Average battery drain (mAh/day)": avg_battery,
    "Average data usage (MB/day)": avg_data,
    "Count verification": count_verification,
    "Exported CSV file": OUTPUT_CSV,
    "JSON summary file": OUTPUT_JSON,
    "Backup file and size": f"{BACKUP_CSV} ({backup_size_bytes} bytes)"
}

with open(OUTPUT_JSON, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

# --- Final Output Block ---
print("\n=== Assessment Data / Result ===")
for key, val in summary_data.items():
    print(f"{key}: {val}")
