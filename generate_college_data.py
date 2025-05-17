# create_sample_data.py
import pandas as pd
import os

# Sample data for college admissions
data = [
    {"exam": "JEE Main", "college": "IIT Delhi", "branch": "Computer Science", "cutoff_rank": 500},
    {"exam": "JEE Main", "college": "IIT Delhi", "branch": "Electrical Engineering", "cutoff_rank": 800},
    {"exam": "JEE Main", "college": "IIT Bombay", "branch": "Computer Science", "cutoff_rank": 300},
    {"exam": "JEE Main", "college": "IIT Bombay", "branch": "Mechanical Engineering", "cutoff_rank": 1000},
    {"exam": "JEE Advanced", "college": "IIT Madras", "branch": "Computer Science", "cutoff_rank": 200},
    {"exam": "JEE Advanced", "college": "IIT Madras", "branch": "Aerospace Engineering", "cutoff_rank": 900},
    {"exam": "JEE Advanced", "college": "IIT Kanpur", "branch": "Chemical Engineering", "cutoff_rank": 1200},
    {"exam": "BITSAT", "college": "BITS Pilani", "branch": "Computer Science", "cutoff_rank": 100},
    {"exam": "BITSAT", "college": "BITS Pilani", "branch": "Electronics and Communication", "cutoff_rank": 300},
    {"exam": "BITSAT", "college": "BITS Goa", "branch": "Computer Science", "cutoff_rank": 200},
    {"exam": "BITSAT", "college": "BITS Hyderabad", "branch": "Mechanical Engineering", "cutoff_rank": 600}
]

# Create DataFrame
df = pd.DataFrame(data)

# Create directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save to Excel
df.to_excel("data/college_data.xlsx", index=False)

# Also save as JSON for backup
os.makedirs("data/backup", exist_ok=True)
df.to_json("data/backup/college_data.json", orient="records")

print("Sample data files created:")
print("- data/college_data.xlsx")
print("- data/backup/college_data.json")