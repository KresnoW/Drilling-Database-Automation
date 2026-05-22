import pandas as pd

# 1. Load your master drilling database
df = pd.read_excel("output/master_drilling_database.xlsx")

# 2. Filter strictly for "CO" lithology (Coal)
coal_df = df[df["Lithology"].str.upper() == "CO"].copy()

# 3. Ensure all quality columns are properly treated as numeric values
quality_columns = ["CVAR", "TM", "TS", "ASH"]
for col in quality_columns:
    if col in coal_df.columns:
        coal_df[col] = pd.to_numeric(coal_df[col], errors="coerce")

# 4. Group by Seam_Name and calculate the average for all quality parameters
seam_quality = coal_df.groupby("Seam_Name", dropna=False).agg(
    Average_CVAR=("CVAR", "mean"),
    Average_TM_Pct=("TM", "mean"),
    Average_TS_Pct=("TS", "mean"),
    Average_ASH_Pct=("ASH", "mean")
).reset_index()

# 5. Rename columns for clean, professional Excel headers
seam_quality.columns = [
    "Seam_Name", 
    "Average_CVAR", 
    "Average_TM (%)", 
    "Average_TS (%)", 
    "Average_ASH (%)"
]

# 6. Round all numeric quality values to 2 decimal places
numeric_cols = ["Average_CVAR", "Average_TM (%)", "Average_TS (%)", "Average_ASH (%)"]
seam_quality[numeric_cols] = seam_quality[numeric_cols].round(2)

# 7. Sort by CVAR ascending (Lowest Quality -> Highest Quality/Rank at the bottom)
seam_quality = seam_quality.sort_values(by="Average_CVAR", ascending=True)

# 8. Export to your output folder
seam_quality.to_excel("output/seam_quality_ranking.xlsx", index=False)

print("Seam complete quality ranking created successfully!")
print("\nPreview of the Quality Ranking (Sorted by CVAR Ascending):")
print(seam_quality)