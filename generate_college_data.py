import pandas as pd
import os

data = [
    {"exam": "JEE Main", "college": "IIT Delhi", "branch": "Computer Science", "cutoff_rank": 500},
    {"exam": "JEE Main", "college": "IIT Bombay", "branch": "Electrical Engineering", "cutoff_rank": 800},
    {"exam": "JEE Advanced", "college": "IIT Madras", "branch": "Mechanical Engineering", "cutoff_rank": 1200},
    {"exam": "BITSAT", "college": "BITS Pilani", "branch": "Computer Science", "cutoff_rank": 100}
]

df = pd.DataFrame(data)
os.makedirs("data", exist_ok=True)
df.to_excel("data/college_data.xlsx", index=False)
os.makedirs("data/backup", exist_ok=True)
df.to_json("data/backup/college_data.json", orient="records")

print("Sample data files created: data/college_data.xlsx, data/backup/college_data.json")