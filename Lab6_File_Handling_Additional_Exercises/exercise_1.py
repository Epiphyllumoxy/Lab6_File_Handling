import csv
import json
import os
import shutil
from collections import Counter


# My Inputs
SEED_DIGIT = 8  # Replace with your seed digit
ID_SUM = 28     # Replace with your ID sum


# Derived Rules
RECORDS_TO_PROCESS = 1000 + ID_SUM
TARGET_CLASS_DIGIT = (SEED_DIGIT % 4) + 2
TARGET_CLASS_PREFIX = f"{TARGET_CLASS_DIGIT}"  # e.g., '2', '3', '4', '5'

# File paths
INPUT_FILE = "weblog.csv"
OUTPUT_CSV = "filtered_weblog.csv"
OUTPUT_JSON = "log_summary.json"
BACKUP_JSON = "log_summary_backup.json"

print(f"--- Running Exercise 1 Analysis ---")
print(f"Targeting first {RECORDS_TO_PROCESS} records.")
print(f"Target HTTP status class: {TARGET_CLASS_PREFIX}xx")

# Data structures for tracking
selected_records = []
status_counter = Counter()
url_counter = Counter()
total_processed = 0

# 1. Read CSV line-by-line without loading entire dataset into memory
if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} not found. Please place it in the same directory.")
    exit()

with open(INPUT_FILE, mode="r", encoding="utf-8") as infile:
    # Use csv.reader or csv.DictReader for clean line-by-line streaming
    reader = csv.DictReader(infile)
    
    # Standardize column naming checks (handling potential whitespace or case mismatches)
    fields = [f.strip() for f in reader.fieldnames]
    status_col = "Staus" if "Staus" in reader.fieldnames else "Status"
    
    for row in reader:
        if total_processed >= RECORDS_TO_PROCESS:
            break
        
        total_processed += 1
        
        # 2. Extract key fields and handle invalid or missing data smoothly
        ip = row.get("IP", "").strip()
        time = row.get("Time", "").strip()
        url = row.get("URL", "").strip()
        status = row.get(status_col, "").strip()
        
        if not ip or not status:
            continue  # Skip missing or corrupted row fragments
            
        # 3. Filter based on target status class prefix (e.g., starts with '2')
        if status.startswith(TARGET_CLASS_PREFIX):
            selected_records.append({
                "IP": ip,
                "Time": time,
                "URL": url,
                "Staus": status
            })
            
            # 4. Update metrics for counting
            status_counter[status] += 1
            url_counter[url] += 1

# Extract five most frequently requested URLs
top_5_urls = [url for url, count in url_counter.most_common(5)]

# 5. Export selected records to a filtered CSV
with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["IP", "Time", "URL", "Staus"])
    writer.writeheader()
    writer.writerows(selected_records)

# Create summary payload
summary_data = {
    "Records processed": total_processed,
    "Target status class": f"{TARGET_CLASS_PREFIX}xx",
    "Records in target class": len(selected_records),
    "Count per status code": dict(status_counter),
    "Five most requested URLs": top_5_urls,
    "Filtered CSV file": OUTPUT_CSV,
    "JSON summary file": OUTPUT_JSON,
    "Backup verification": "Pending"
}

# Write summary to JSON
with open(OUTPUT_JSON, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

# 6. Create a backup of the JSON file and verify its existence
shutil.copyfile(OUTPUT_JSON, BACKUP_JSON)
backup_exists = os.path.exists(BACKUP_JSON)

# Update JSON summary to reflect backup verification status
summary_data["Backup verification"] = "Verified" if backup_exists else "Failed"
with open(OUTPUT_JSON, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

# --- Final Output Block ---
print("\n=== Assessment Data / Result ===")
for key, val in summary_data.items():
    print(f"{key}: {val}")
