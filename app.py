import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page config
st.set_page_config(
    page_title="Coal Drilling Dashboard",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1a5276;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a5276 0%, #2874a6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all pipeline output files."""
    master_df = pd.read_excel("output/master_drilling_database.xlsx")
    seam_quality = pd.read_excel("output/seam_quality_ranking.xlsx")
    lith_summary = pd.read_excel("output/lithology_percentage_summary.xlsx")
    rig_totals = pd.read_excel("output/rig_drilling_totals.xlsx")
    seam_thickness = pd.read_excel("output/seam_thickness_summary.xlsx")
    return master_df, seam_quality, lith_summary, rig_totals, seam_thickness

try:
    master_df, seam_quality, lith_summary, rig_totals, seam_thickness = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run the pipeline first: python run_all.py")
    data_loaded = False

if data_loaded:
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/mining.png", width=80)
        st.title("Drilling Dashboard")
        st.markdown("---")

        # Filters
        st.subheader("🔍 Filters")

        selected_rigs = st.multiselect(
            "Select Rigs",
            options=sorted(master_df['RIG'].unique()),
            default=sorted(master_df['RIG'].unique())[:5]
        )

        selected_lith = st.multiselect(
            "Select Lithology",
            options=sorted(master_df['Lithology'].unique()),
            default=['CO', 'TUFF', 'CARB', 'SS']
        )

        depth_range = st.slider(
            "Depth Range (m)",
            float(master_df['Depth_From'].min()),
            float(master_df['Depth_To'].max()),
            (0.0, float(master_df['Depth_To'].max()))
        )

        st.markdown("---")
        st.markdown("**By:** Kresno")
        st.markdown("[GitHub Repo](https://github.com/KresnoW/Drilling-Database-Automation)")

    # Filter data
    filtered_df = master_df[
        (master_df['RIG'].isin(selected_rigs)) &
        (master_df['Lithology'].isin(selected_lith)) &
        (master_df['Depth_From'] >= depth_range[0]) &
        (master_df['Depth_To'] <= depth_range[1])
    ]

    # Main Header
    st.markdown('<p class="main-header">⛏️ Coal Drilling Operations Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time analytics from drilling database pipeline</p>', unsafe_allow_html=True)

    # Key Metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("🚧 Active Rigs", len(selected_rigs), f"of {master_df['RIG'].nunique()} total")
    with col2:
        total_depth = filtered_df['CalcThick'].sum()
        st.metric("📏 Total Depth", f"{total_depth:,.1f}m")
    with col3:
        st.metric("📊 Intervals", len(filtered_df))
    with col4:
        coal_count = len(filtered_df[filtered_df['Lithology'].str.upper() == 'CO'])
        st.metric("💎 Coal Found", coal_count)
    with col5:
        unique_seams = filtered_df[filtered_df['Lithology'].str.upper() == 'CO']['Seam_Name'].dropna().nunique()
        st.metric("⛰️ Seams", unique_seams)
    with col6:
        st.metric("🧪 Lith Types", len(selected_lith))

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Rig Performance", 
        "🧪 Lithology", 
        "💎 Coal Quality", 
        "📏 Seam Thickness",
        "📋 Raw Data"
    ])

    # Tab 1: Rig Performance
    with tab1:
        st.subheader("Rig Performance Analysis")

        col_left, col_right = st.columns(2)

        with col_left:
            rig_depth = filtered_df.groupby('RIG')['CalcThick'].sum().sort_values(ascending=True)
            fig = px.bar(
                x=rig_depth.values,
                y=rig_depth.index,
                orientation='h',
                title="Total Depth Drilled by Rig",
                labels={'x': 'Depth (m)', 'y': 'Rig'},
                color=rig_depth.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            rig_intervals = filtered_df.groupby('RIG').size().sort_values(ascending=True)
            fig2 = px.bar(
                x=rig_intervals.values,
                y=rig_intervals.index,
                orientation='h',
                title="Intervals Drilled by Rig",
                labels={'x': 'Count', 'y': 'Rig'},
                color=rig_intervals.values,
                color_continuous_scale='Greens'
            )
            fig2.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Rig Summary Table")
        rig_summary = filtered_df.groupby('RIG').agg({
            'CalcThick': ['sum', 'mean', 'count'],
            'Depth_From': 'min',
            'Depth_To': 'max'
        }).round(2)
        rig_summary.columns = ['Total Depth', 'Avg Thickness', 'Intervals', 'Min Depth', 'Max Depth']
        rig_summary = rig_summary.sort_values('Total Depth', ascending=False)
        st.dataframe(rig_summary, use_container_width=True)

    # Tab 2: Lithology
    with tab2:
        st.subheader("Lithology Distribution")

        col_left, col_right = st.columns(2)

        with col_left:
            lith_counts = filtered_df['Lithology'].value_counts()
            # Custom colors - CO (coal) is BLACK
            color_map = {
                'CO': '#000000',
                'TUFF': '#7fcdbb',
                'CARB': '#fec44f',
                'SS': '#bcbddc',
                'MS': '#fd8d3c',
                'SILT': '#74c476',
                'CL': '#41b6c4',
                'SH': '#225ea8',
                'SLT': '#9e9ac8',
                'CB': '#e34a33'
            }
            fig = px.pie(
                values=lith_counts.values,
                names=lith_counts.index,
                title="Lithology Distribution",
                hole=0.4,
                color=lith_counts.index,
                color_discrete_map=color_map
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            fig2 = px.bar(
    x=lith_counts.index,
    y=lith_counts.values,
    title="Interval Count by Lithology",
    labels={'x': 'Lithology', 'y': 'Count'},
    color=lith_counts.index,
    color_discrete_map=color_map
)
            fig2.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Depth Distribution by Lithology")
        lith_depth = filtered_df.groupby('Lithology')['CalcThick'].sum().sort_values(ascending=False)
        fig3 = px.bar(
    x=lith_depth.index,
    y=lith_depth.values,
    title="Total Thickness by Lithology",
    labels={'x': 'Lithology', 'y': 'Total Thickness (m)'},
    color=lith_depth.index,
    color_discrete_map=color_map
)
        st.plotly_chart(fig3, use_container_width=True)

    # Tab 3: Coal Quality
    with tab3:
        st.subheader("Coal Seam Quality Analysis")

        def classify_quality(row):
            if row['Average_CVAR'] >= 6500 and row['Average_ASH (%)'] < 15:
                return 'Premium'
            elif row['Average_CVAR'] >= 5500:
                return 'Standard'
            else:
                return 'Low'

        seam_quality['Quality_Class'] = seam_quality.apply(classify_quality, axis=1)

        col_left, col_right = st.columns(2)

        with col_left:
            fig = px.bar(
                seam_quality.sort_values('Average_CVAR', ascending=True),
                x='Average_CVAR',
                y='Seam_Name',
                orientation='h',
                title="Coal Seam Quality Ranking (CVAR)",
                labels={'Average_CVAR': 'CVAR (kcal/kg)', 'Seam_Name': 'Seam'},
                color='Average_CVAR',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            quality_counts = seam_quality['Quality_Class'].value_counts()
            colors_map = {'Premium': '#27ae60', 'Standard': '#f39c12', 'Low': '#e74c3c'}
            fig2 = px.pie(
                values=quality_counts.values,
                names=quality_counts.index,
                title="Quality Classification",
                color=quality_counts.index,
                color_discrete_map=colors_map,
                hole=0.4
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Multi-Parameter Quality Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            fig = px.scatter(
                seam_quality, x='Average_TM (%)', y='Average_CVAR',
                color='Quality_Class', size='Average_CVAR',
                hover_data=['Seam_Name'],
                title="CVAR vs Total Moisture",
                color_discrete_map=colors_map
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(
                seam_quality, x='Average_ASH (%)', y='Average_CVAR',
                color='Quality_Class', size='Average_CVAR',
                hover_data=['Seam_Name'],
                title="CVAR vs Ash Content",
                color_discrete_map=colors_map
            )
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            fig = px.scatter(
                seam_quality, x='Average_TS (%)', y='Average_CVAR',
                color='Quality_Class', size='Average_CVAR',
                hover_data=['Seam_Name'],
                title="CVAR vs Total Sulfur",
                color_discrete_map=colors_map
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Complete Quality Table")
        display_df = seam_quality[['Seam_Name', 'Average_CVAR', 'Average_TM (%)', 'Average_TS (%)', 'Average_ASH (%)', 'Quality_Class']].copy()
        display_df.columns = ['Seam', 'CVAR', 'TM (%)', 'TS (%)', 'ASH (%)', 'Class']

        def color_class(val):
            if val == 'Premium':
                return 'background-color: #d5f5e3; color: #27ae60; font-weight: bold'
            elif val == 'Standard':
                return 'background-color: #fdebd0; color: #f39c12; font-weight: bold'
            else:
                return 'background-color: #fadbd8; color: #e74c3c; font-weight: bold'

        st.dataframe(
            display_df.style.map(color_class, subset=['Class']),
            use_container_width=True,
            height=400
        )

    # Tab 4: Seam Thickness
    with tab4:
        st.subheader("Coal Seam Thickness Analysis")

        seam_agg = seam_thickness.groupby('Seam_Name').agg({
            'CalcThick': ['sum', 'mean', 'count'],
            'RIG': lambda x: ', '.join(sorted(x.unique()))
        }).reset_index()
        seam_agg.columns = ['Seam_Name', 'Total_Thickness', 'Avg_Thickness', 'Occurrences', 'Rigs']
        seam_agg = seam_agg.sort_values('Total_Thickness', ascending=False)

        col_left, col_right = st.columns(2)

        with col_left:
            top_15 = seam_agg.head(15)
            fig = px.bar(
                top_15,
                x='Seam_Name',
                y='Total_Thickness',
                title="Top 15 Seams by Total Thickness",
                labels={'Total_Thickness': 'Thickness (m)', 'Seam_Name': 'Seam'},
                color='Total_Thickness',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            fig2 = px.scatter(
                seam_agg,
                x='Occurrences',
                y='Total_Thickness',
                size='Avg_Thickness',
                hover_data=['Seam_Name', 'Rigs'],
                title="Occurrences vs Total Thickness",
                labels={'Occurrences': 'Drill Intersections', 'Total_Thickness': 'Total Thickness (m)'},
                color='Avg_Thickness',
                color_continuous_scale='Viridis'
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Seam Thickness Summary")
        display_agg = seam_agg.copy()
        display_agg.columns = ['Seam', 'Total (m)', 'Average (m)', 'Occurrences', 'Rigs Present']
        st.dataframe(display_agg, use_container_width=True, height=400)

    # Tab 5: Raw Data
    with tab5:
        st.subheader("Raw Drilling Data Explorer")

        st.markdown(f"**Showing {len(filtered_df)} of {len(master_df)} total records**")

        cols = st.multiselect(
            "Select columns to display",
            options=list(master_df.columns),
            default=['HoleID', 'RIG', 'Seam_Name', 'Depth_From', 'Depth_To', 'CalcThick', 'Lithology', 'CVAR', 'ASH']
        )

        st.dataframe(filtered_df[cols], use_container_width=True, height=500)

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_drilling_data.csv',
            mime='text/csv'
        )

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>"
        "Built with Streamlit + Plotly | Data from Drilling Database Automation Pipeline | Kresno © 2026"
        "</p>",
        unsafe_allow_html=True
    )
    