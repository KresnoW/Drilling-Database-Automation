import pandas as pd
import glob

# Find CSV files
files = glob.glob("data/*.csv")

# Add Excel files
files += glob.glob("data/*.xlsx")

# Empty dataframe list
df_list = []

# Read all files
for file in files:
    try:
        # CSV files
        if file.endswith(".csv"):
            df = pd.read_csv(file, sep=";")
            # Retry with comma delimiter
            if len(df.columns) == 1:
                df = pd.read_csv(file, sep=",")

        # Excel files
        elif file.endswith(".xlsx"):
            df = pd.read_excel(file)

        # Add dataframe into list
        df_list.append(df)
        print(f"Loaded: {file}")

    except Exception as e:
        print(f"Error reading: {file}")
        print(e)

# Combine all dataframes
combined_df = pd.concat(df_list, ignore_index=True)

# Remove duplicates
combined_df = combined_df.drop_duplicates()

# Convert thickness column to numeric
combined_df["CalcThick"] = pd.to_numeric(
    combined_df["CalcThick"],
    errors="coerce"
)

# --- CLEANING & SORTING THE MASTER DATABASE ---
# Arrange the entire master database by rig number cleanly
combined_df = combined_df.sort_values(by="RIG", ascending=True)


# --- PROCESSING THE COAL SEAM SUMMARY ---
# 1. Filter strictly for "CO" lithology (exact match, case-insensitive)
coal_df = combined_df[combined_df["Lithology"].str.upper() == "CO"]

# --- PROCESSING THE COAL SEAM SUMMARY ---
# 1. Filter strictly for "CO" lithology (exact match, case-insensitive)
coal_df = combined_df[combined_df["Lithology"].str.upper() == "CO"]

# 2. Group by multiple columns (Added "RIG" to the list)
seam_summary = coal_df.groupby(
    ["RIG", "Seam_Name", "Depth_From", "Depth_To"], 
    dropna=False
)[["CalcThick"]].sum()

# 3. Convert to a clean dataframe by resetting the index
seam_summary = seam_summary.reset_index()

# 4. Round the calculated thickness values to 2 decimal places
seam_summary["CalcThick"] = seam_summary["CalcThick"].round(2)

# 5. Cleanly sort by Rig, Seam_Name, and Depth_From for structure
seam_summary = seam_summary.sort_values(by=["RIG", "Seam_Name", "Depth_From"])


# --- EXPORT OUTPUTS ---
# Export Seam Summary
seam_summary.to_excel(
    "output/seam_thickness_summary.xlsx", 
    index=False
)

# Export Sorted Master Database
combined_df.to_excel(
    "output/master_drilling_database.xlsx",
    index=False
)

print("Coal Summary Successfully Created!")