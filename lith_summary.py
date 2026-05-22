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

# 3. Calculate counts and percentages
# value_counts(normalize=True) gives fractions; multiplying by 100 turns them into percentages
litho_counts = df["Lithology"].value_counts()
litho_pct = df["Lithology"].value_counts(normalize=True) * 100

# 4. Combine counts and percentages into a neat summary DataFrame
# value_counts automatically sorts from highest percentage to lowest!
litho_summary = pd.DataFrame({
    "Lithology": litho_counts.index,
    "Total_Interval_Count": litho_counts.values,
    "Percentage": litho_pct.values
})

# 5. Round and format with the '%' sign
litho_summary["Percentage"] = litho_summary["Percentage"].round(2).astype(str) + "%"

# 6. Export to your output folder
litho_summary.to_excel("output/lithology_percentage_summary.xlsx", index=False)

print("Lithology percentage summary created successfully!")
print("\nPreview of the data:")
print(litho_summary)