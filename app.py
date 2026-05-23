import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Drilling Dashboard", layout="wide")

st.title("Mining Drilling Database Dashboard")

rig_totals = pd.read_excel("output/rig_drilling_totals.xlsx")

st.subheader("Rig Performance")
st.dataframe(rig_totals)

fig, ax = plt.subplots()

ax.bar(
    rig_totals["RIG"],
    rig_totals["Total_Depth_Drilled"]
)

ax.set_ylabel("Depth Drilled")
ax.set_title("Total Depth by Rig")

st.pyplot(fig)