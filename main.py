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
combined_df = pd.concat(
    df_list,
    ignore_index=True
)

# Remove duplicates
combined_df = combined_df.drop_duplicates()

# Convert thickness column to numeric
combined_df["CalcThick"] = pd.to_numeric(
    combined_df["CalcThick"],
    errors="coerce"
)

# Filter coal intervals
coal_df = combined_df[
    combined_df["Lithology"].str.contains(
        "CO",
        case=False,
        na=False
    )
]

# Arrange by rig number
coal_df = coal_df.sort_values(
    by="RIG",
    ascending=True
)

# Coal thickness summary
coal_summary = coal_df.groupby("RIG")[
    "CalcThick"
].sum()

# Convert to dataframe
coal_summary = coal_summary.reset_index()

# Rename columns
coal_summary.columns = [
    "RIG",
    "Total_Coal_Thickness"
]

# Export outputs
combined_df.to_excel(
    "output/master_drilling_database.xlsx",
    index=False
)

print("Database Successfully Created!")