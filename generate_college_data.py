import pandas as pd
import os

# Define 5 selected IIITs (including IIIT Naya Raipur) and their B.Tech branches (NIRF 2024 or JoSAA)
colleges_data = [
    {
        "college": "IIIT Bangalore",
        "exam": "JEE Main",
        "branches": [
            {"name": "Computer Science and Engineering", "cutoff_rank": 3500, "avg_placement": 21, "med_placement": 19, "high_placement": 48},
            {"name": "Electronics and Communication Engineering", "cutoff_rank": 6000, "avg_placement": 17, "med_placement": 15, "high_placement": 38},
        ],
    },
    {
        "college": "ABV-IIITM Gwalior",
        "exam": "JEE Main",
        "branches": [
            {"name": "Computer Science and Engineering", "cutoff_rank": 7000, "avg_placement": 18, "med_placement": 16, "high_placement": 40},
            {"name": "Information Technology", "cutoff_rank": 8500, "avg_placement": 17, "med_placement": 15, "high_placement": 38},
            {"name": "Electronics and Communication Engineering", "cutoff_rank": 12000, "avg_placement": 15, "med_placement": 14, "high_placement": 32},
        ],
    },
    {
        "college": "IIITDM Jabalpur",
        "exam": "JEE Main",
        "branches": [
            {"name": "Computer Science and Engineering", "cutoff_rank": 9000, "avg_placement": 17, "med_placement": 15, "high_placement": 38},
            {"name": "Electronics and Communication Engineering", "cutoff_rank": 14000, "avg_placement": 14, "med_placement": 13, "high_placement": 30},
            {"name": "Mechanical Engineering", "cutoff_rank": 30000, "avg_placement": 12, "med_placement": 11, "high_placement": 25},
            {"name": "Smart Manufacturing", "cutoff_rank": 35000, "avg_placement": 11, "med_placement": 10, "high_placement": 22},
        ],
    },
    {
        "college": "IIITDM Kancheepuram",
        "exam": "JEE Main",
        "branches": [
            {"name": "Computer Science and Engineering", "cutoff_rank": 10000, "avg_placement": 16, "med_placement": 14, "high_placement": 35},
            {"name": "Electronics and Communication Engineering", "cutoff_rank": 16000, "avg_placement": 14, "med_placement": 13, "high_placement": 30},
            {"name": "Mechanical Engineering", "cutoff_rank": 32000, "avg_placement": 12, "med_placement": 11, "high_placement": 25},
            {"name": "Smart Manufacturing", "cutoff_rank": 36000, "avg_placement": 11, "med_placement": 10, "high_placement": 22},
        ],
    },
    {
        "college": "IIIT Naya Raipur",
        "exam": "JEE Main",
        "branches": [
            {"name": "Computer Science and Engineering", "cutoff_rank": 21000, "avg_placement": 18, "med_placement": 16, "high_placement": 82},
            {"name": "Electronics and Communication Engineering", "cutoff_rank": 37000, "avg_placement": 14, "med_placement": 13, "high_placement": 30},
            {"name": "Data Science and Artificial Intelligence", "cutoff_rank": 25000, "avg_placement": 17, "med_placement": 15, "high_placement": 40},
        ],
    },
]

# Read existing Excel file
input_path = "E:\\gradguide-backend\\data\\college_data.xlsx"
existing_df = pd.read_excel(input_path)

# Create new data
new_data = []
for college in colleges_data:
    for branch in college["branches"]:
        new_data.append({
            "exam": college["exam"],
            "college": college["college"],
            "branch": branch["name"],
            "cutoff_rank": branch["cutoff_rank"],
            "average_placement": branch["avg_placement"],
            "median_placement": branch["med_placement"],
            "highest_placement": branch["high_placement"],
        })

new_df = pd.DataFrame(new_data)

# Ensure integer types for placement and cutoff fields
new_df["cutoff_rank"] = new_df["cutoff_rank"].astype(int)
new_df["average_placement"] = new_df["average_placement"].astype(int)
new_df["median_placement"] = new_df["median_placement"].astype(int)
new_df["highest_placement"] = new_df["highest_placement"].astype(int)

# Append new data to existing data
combined_df = pd.concat([existing_df, new_df], ignore_index=True)

# Define output path
output_path = "E:\\gradguide-backend\\data\\college_data.xlsx"

# Save to Excel
combined_df.to_excel(output_path, index=False)
print(f"Appended data for 5 IIITs (including IIIT Naya Raipur) to {output_path}")