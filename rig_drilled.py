import pandas as pd

# 1. Load your master drilling database
df = pd.read_excel("output/master_drilling_database.xlsx")

# 2. Group by RIG and aggregate both the count of intervals and sum of CalcThick
rig_summary = df.groupby("RIG", dropna=False).agg(
    Total_Intervals_Drilled=("RIG", "count"),
    Total_Depth_Drilled=("CalcThick", "sum")
).reset_index()

# 3. Round the total depth to 2 decimal places
rig_summary["Total_Depth_Drilled"] = rig_summary["Total_Depth_Drilled"].round(2)

# 4. Sort from the rig that drilled the most total intervals to the least
rig_summary = rig_summary.sort_values(by="Total_Intervals_Drilled", ascending=False)

# 5. Organize columns in a clean order by rig number, total intervals, and total depth
rig_summary = rig_summary[["RIG", "Total_Intervals_Drilled", "Total_Depth_Drilled"]]

# 6. Sort from the rig that drilled the most total depth to the least
rig_summary = rig_summary.sort_values(by="Total_Depth_Drilled", ascending=False)

# 7. Export to your output folder
rig_summary.to_excel("output/rig_drilling_totals.xlsx", index=False)

print("Rig drilling totals summary created successfully!")
print("\nPreview of the data:")
print(rig_summary)