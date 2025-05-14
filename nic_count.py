import csv
from collections import Counter

# Load CSV data
results = []
with open("nic_report.csv", mode="r", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        results.append(row)

# Count NIC types
nic_type_counts = Counter(row["nic_type"] for row in results)

# Print summary
print("NIC Type Summary:")
for nic_type, count in nic_type_counts.items():
    print(f"{nic_type}: {count}")
