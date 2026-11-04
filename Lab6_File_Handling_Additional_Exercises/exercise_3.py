import csv
import json
import os
import shutil
from collections import Counter

# My Inputs
SEED_DIGIT = 8  

# Derived Rules (from Page 15)
TARGET_YEAR = 2015 + SEED_DIGIT

# File paths (from Page 16)
INPUT_FILE = "Global_Cybersecurity_Threats_2015-2024.csv"
OUTPUT_CSV = "filtered_cybersecurity_incidents.csv"
OUTPUT_JSON = "cybersecurity_summary.json"
BACKUP_JSON = "cybersecurity_summary_backup.json"
REPORT_TXT = "cybersecurity_report.txt"

print(f"--- Running Exercise 3 Analysis ---")
print(f"Target Year: {TARGET_YEAR}")

if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} not found. Please place it in the same directory.")
    exit()

# Tracking structures
total_records_processed = 0
selected_incidents = []
attack_type_counter = Counter()
total_financial_loss = 0.0

# 1. Read the CSV file and select incidents occurring in the target year
with open(INPUT_FILE, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    
    # Map exact column names from the specifications
    columns = reader.fieldnames if reader.fieldnames else []
    year_col = "Year" if "Year" in columns else "Incident Year"
    attack_col = "Attack Type"
    loss_col = "Financial Loss (in Million $)"

    for row in reader:
        total_records_processed += 1
        
        raw_year = row.get(year_col, "").strip()
        attack_type = row.get(attack_col, "").strip()
        raw_loss = row.get(loss_col, "").strip()
        
        if str(TARGET_YEAR) in raw_year:
            # Handle invalid financial values and empty strings appropriately
            try:
                loss_value = float(raw_loss) if raw_loss else 0.0
            except ValueError:
                loss_value = 0.0  
                
            total_financial_loss += loss_value
            
            # 2. Count the incidents belonging to each attack type
            if attack_type:
                attack_type_counter[attack_type] += 1
            
            # Save relevant details while appending a record index tracking field
            selected_incidents.append({
                "Original_Order": total_records_processed,
                "Incident ID": row.get("Incident ID", f"INC-{total_records_processed}").strip(),
                "Year": raw_year,
                "Attack Type": attack_type,
                "Financial Loss (in Million $)": loss_value,
                "Country": row.get("Country", "Unknown").strip(),
                "Target Industry": row.get("Target Industry", "Unknown").strip()
            })

# 3. Calculate the total and average financial loss of the selected incidents
incidents_count = len(selected_incidents)
average_financial_loss = (total_financial_loss / incidents_count) if incidents_count > 0 else 0.0

# 4. Identify the five incidents with the highest financial losses
# Uses Python's stable Timsort algorithm to retain the original dataset order when losses are tied
sorted_by_loss = sorted(
    selected_incidents, 
    key=lambda x: x["Financial Loss (in Million $)"], 
    reverse=True
)
top_5_costliest = sorted_by_loss[:5]

# Clean up internal sorting trackers before writing out to file logs
for item in selected_incidents:
    item.pop("Original_Order", None)
for item in top_5_costliest:
    item.pop("Original_Order", None)

# 5. Export the selected incidents to a filtered CSV file
fieldnames_to_export = ["Incident ID", "Year", "Attack Type", "Financial Loss (in Million $)", "Country", "Target Industry"]
with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames_to_export)
    writer.writeheader()
    writer.writerows(selected_incidents)

# Export records and summary metadata to JSON file
summary_data = {
    "Target year": TARGET_YEAR,
    "Total records in dataset": total_records_processed,
    "Incidents in target year": incidents_count,
    "Count per attack type": dict(attack_type_counter),
    "Total financial loss (USD millions)": round(total_financial_loss, 2),
    "Average financial loss (USD millions)": round(average_financial_loss, 2),
    "Five costliest incidents": top_5_costliest,
    "Filtered CSV file": OUTPUT_CSV,
    "JSON summary file": OUTPUT_JSON,
    "Backup verification": "Pending",
    "Report file": REPORT_TXT
}

with open(OUTPUT_JSON, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

# Create a verified backup of the JSON file
shutil.copyfile(OUTPUT_JSON, BACKUP_JSON)
backup_exists = os.path.exists(BACKUP_JSON)

# Update internal item to match the assessment verification requirement field
summary_data["Backup verification"] = "Verified" if backup_exists else "Failed"
with open(OUTPUT_JSON, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

# 6. Generate a text report containing counts, financial losses, five costliest incidents, and file info
report_content = f"""CYBERSECURITY INCIDENT REPORT SUMMARY
==================================================
Target Year Evaluation: {TARGET_YEAR}
Total Records in Dataset: {total_records_processed}
Total Incidents in Target Year: {incidents_count}

Financial Summary:
--------------------------------------------------
Total Financial Loss: ${total_financial_loss:,.2f} Million USD
Average Financial Loss: ${average_financial_loss:,.2f} Million USD

Distribution Count Per Attack Type:
--------------------------------------------------
"""
for attack, count in attack_type_counter.items():
    report_content += f"- {attack}: {count} incident(s)\n"

report_content += """
Five Costliest Incidents:
--------------------------------------------------
"""
for idx, inc in enumerate(top_5_costliest, 1):
    report_content += f"{idx}. ID: {inc.get('Incident ID')} | Industry: {inc.get('Target Industry')} | Loss: ${inc.get('Financial Loss (in Million $)')}M\n"

report_content += f"""
Generated Output Documentation:
--------------------------------------------------
- Filtered Dataset: {OUTPUT_CSV}
- JSON Overview: {OUTPUT_JSON}
- Backup Log: {BACKUP_JSON} (Status: {summary_data['Backup verification']})
==================================================
"""

with open(REPORT_TXT, mode="w", encoding="utf-8") as report_file:
    report_file.write(report_content.strip())

# --- Final Output Block ---
print("\n=== Assessment Data / Result ===")
for key, val in summary_data.items():
    if key != "Five costliest incidents":
        print(f"{key}: {val}")
    else:
        print(f"{key}: [Listed {len(val)} costliest records inside JSON]")
