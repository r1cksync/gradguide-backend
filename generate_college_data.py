import pandas as pd
import os
import random

# Create directory for data if it doesn't exist
os.makedirs("data", exist_ok=True)

# List of exams
exams = ["JEE Mains", "JEE Advanced", "BITSAT"]

# List of top colleges
colleges = {
    "JEE Mains": [
        "NIT Trichy", "NIT Warangal", "NIT Surathkal", "NIT Rourkela", 
        "IIIT Hyderabad", "IIIT Delhi", "IIIT Bangalore", 
        "DTU Delhi", "NSIT Delhi", "PEC Chandigarh"
    ],
    "JEE Advanced": [
        "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", 
        "IIT Kharagpur", "IIT Roorkee", "IIT Guwahati", 
        "IIT Hyderabad", "IIT BHU", "IIT Indore"
    ],
    "BITSAT": [
        "BITS Pilani", "BITS Hyderabad", "BITS Goa"
    ]
}

# List of branches
branches = [
    "Computer Science and Engineering", 
    "Electronics and Communication Engineering",
    "Mechanical Engineering", 
    "Electrical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Aerospace Engineering",
    "Biotechnology"
]

# Rank ranges for different exams
rank_ranges = {
    "JEE Mains": (1, 50000),
    "JEE Advanced": (1, 20000),
    "BITSAT": (1, 10000)
}

# Generate data
data = []

# For each exam
for exam in exams:
    # For each college for this exam
    for college in colleges[exam]:
        # For each branch
        for branch in branches:
            # Generate a realistic cutoff rank
            if branch == "Computer Science and Engineering":
                # CS usually has the lowest cutoffs (best ranks)
                rank_min, rank_max = rank_ranges[exam]
                cutoff = random.randint(rank_min, int(rank_max * 0.3))
            elif branch in ["Electronics and Communication Engineering", "Electrical Engineering"]:
                # ECE and EE have the next best ranks
                rank_min, rank_max = rank_ranges[exam]
                cutoff = random.randint(int(rank_max * 0.2), int(rank_max * 0.5))
            else:
                # Other branches have higher cutoffs
                rank_min, rank_max = rank_ranges[exam]
                cutoff = random.randint(int(rank_max * 0.4), rank_max)
            
            # Add to our data
            data.append({
                "exam": exam,
                "college": college,
                "branch": branch,
                "cutoff_rank": cutoff
            })

# Create DataFrame
df = pd.DataFrame(data)

# Sort by exam, then by cutoff rank
df = df.sort_values(by=["exam", "cutoff_rank"])

# Save to Excel
df.to_excel("data/college_data.xlsx", index=False)

print(f"Generated college_data.xlsx with {len(df)} entries")
print(f"File saved at: {os.path.abspath('data/college_data.xlsx')}")