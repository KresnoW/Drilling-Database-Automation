#!/usr/bin/env python3
"""
Daily Drilling Rig PDF Report Generator
Integrates with existing pipeline: main.py -> coal_summary.py -> coal_rank.py -> lith_summary.py -> rig_drilled.py

Usage:
    python daily_report.py

Requirements:
    pip install pandas matplotlib reportlab openpyxl
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def create_daily_drilling_report(output_dir="output", data_dir="data"):
    """Generate a comprehensive daily drilling PDF report from pipeline outputs."""

    # Load all pipeline outputs
    master_df = pd.read_excel(f"{output_dir}/master_drilling_database.xlsx")
    seam_quality = pd.read_excel(f"{output_dir}/seam_quality_ranking.xlsx")
    lith_summary = pd.read_excel(f"{output_dir}/lithology_percentage_summary.xlsx")
    rig_totals = pd.read_excel(f"{output_dir}/rig_drilling_totals.xlsx")
    seam_thickness = pd.read_excel(f"{output_dir}/seam_thickness_summary.xlsx")

    report_date = datetime.now().strftime("%Y-%m-%d")
    pdf_path = f"{output_dir}/daily_drilling_report_{report_date}.pdf"

    # Initialize document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'], fontSize=24,
        textColor=colors.HexColor('#1a5276'), spaceAfter=12,
        alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'], fontSize=16,
        textColor=colors.HexColor('#2874a6'), spaceAfter=10,
        spaceBefore=12, fontName='Helvetica-Bold'
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading', parent=styles['Heading3'], fontSize=13,
        textColor=colors.HexColor('#2e86c1'), spaceAfter=8,
        spaceBefore=10, fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'], fontSize=10,
        leading=14, alignment=TA_LEFT
    )

    # ==================== PAGE 1: TITLE & EXECUTIVE SUMMARY ====================
    story.append(Paragraph("DAILY DRILLING OPERATIONS REPORT", title_style))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", 
                          ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=TA_CENTER, 
                                         fontSize=12, textColor=colors.grey, spaceAfter=20)))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))

    total_rigs = rig_totals['RIG'].nunique()
    total_depth = rig_totals['Total_Depth_Drilled'].sum()
    total_intervals = rig_totals['Total_Intervals_Drilled'].sum()
    total_coal_intervals = len(master_df[master_df['Lithology'].str.upper() == 'CO'])
    unique_seams = master_df[master_df['Lithology'].str.upper() == 'CO']['Seam_Name'].dropna().nunique()
    avg_depth_per_rig = rig_totals['Total_Depth_Drilled'].mean()

    summary_data = [
        ['Metric', 'Value'],
        ['Total Active Rigs', f'{total_rigs}'],
        ['Total Depth Drilled (m)', f'{total_depth:,.2f}'],
        ['Total Intervals Drilled', f'{total_intervals:,}'],
        ['Coal Intervals Identified', f'{total_coal_intervals}'],
        ['Unique Coal Seams', f'{unique_seams}'],
        ['Average Depth per Rig (m)', f'{avg_depth_per_rig:,.2f}'],
        ['Report Generation Time', datetime.now().strftime('%H:%M:%S')]
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eaf2f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2874a6')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#eaf2f8'), colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("KEY INSIGHTS", subheading_style))
    insights = [
        f"• <b>Top Performing Rig:</b> {rig_totals.iloc[0]['RIG']} with {rig_totals.iloc[0]['Total_Depth_Drilled']:,.2f}m drilled",
        f"• <b>Most Common Lithology:</b> {lith_summary.iloc[0]['Lithology']} ({lith_summary.iloc[0]['Percentage']})",
        f"• <b>Highest Quality Seam:</b> {seam_quality.iloc[-1]['Seam_Name']} (CVAR: {seam_quality.iloc[-1]['Average_CVAR']:,.2f})",
        f"• <b>Lowest Quality Seam:</b> {seam_quality.iloc[0]['Seam_Name']} (CVAR: {seam_quality.iloc[0]['Average_CVAR']:,.2f})",
    ]
    for insight in insights:
        story.append(Paragraph(insight, body_style))
        story.append(Spacer(1, 0.05*inch))

    story.append(PageBreak())

    # ==================== PAGE 2: RIG PERFORMANCE ====================
    story.append(Paragraph("RIG PERFORMANCE SUMMARY", heading_style))
    story.append(Paragraph("Comprehensive overview of drilling performance by rig.", body_style))
    story.append(Spacer(1, 0.15*inch))

    rig_data = [['RIG', 'Intervals', 'Depth (m)', 'Avg Depth/Interval']]
    for _, row in rig_totals.iterrows():
        avg = row['Total_Depth_Drilled'] / row['Total_Intervals_Drilled'] if row['Total_Intervals_Drilled'] > 0 else 0
        rig_data.append([row['RIG'], f"{row['Total_Intervals_Drilled']}", 
                        f"{row['Total_Depth_Drilled']:,.2f}", f"{avg:.2f}"])

    rig_table = Table(rig_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    rig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf2f8')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rig_table)
    story.append(Spacer(1, 0.2*inch))

    # Generate chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.patch.set_facecolor('white')
    colors_bars = ['#1a5276' if i == 0 else '#2874a6' if i == 1 else '#5dade2' if i == 2 else '#85c1e9' 
                   for i in range(len(rig_totals))]
    ax1.barh(rig_totals['RIG'][::-1], rig_totals['Total_Depth_Drilled'][::-1], color=colors_bars[::-1])
    ax1.set_xlabel('Total Depth Drilled (m)', fontsize=10, fontweight='bold')
    ax1.set_title('Total Depth by Rig', fontsize=12, fontweight='bold', color='#1a5276')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    ax2.barh(rig_totals['RIG'][::-1], rig_totals['Total_Intervals_Drilled'][::-1], color=colors_bars[::-1])
    ax2.set_xlabel('Total Intervals', fontsize=10, fontweight='bold')
    ax2.set_title('Intervals Drilled by Rig', fontsize=12, fontweight='bold', color='#1a5276')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    chart_path = f"{output_dir}/rig_performance_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    story.append(Image(chart_path, width=6.5*inch, height=3*inch))
    story.append(PageBreak())

    # ==================== PAGE 3: LITHOLOGY ====================
    story.append(Paragraph("LITHOLOGY DISTRIBUTION ANALYSIS", heading_style))
    story.append(Spacer(1, 0.15*inch))

    lith_data = [['Lithology', 'Interval Count', 'Percentage']]
    for _, row in lith_summary.iterrows():
        lith_data.append([row['Lithology'], f"{row['Total_Interval_Count']}", row['Percentage']])

    lith_table = Table(lith_data, colWidths=[2*inch, 2*inch, 2*inch])
    lith_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf2f8')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(lith_table)
    story.append(Spacer(1, 0.2*inch))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.patch.set_facecolor('white')
    lith_colors = plt.cm.Set3(np.linspace(0, 1, len(lith_summary)))
    ax1.pie(lith_summary['Total_Interval_Count'], labels=lith_summary['Lithology'], autopct='%1.1f%%',
            startangle=90, colors=lith_colors, textprops={'fontsize': 9, 'fontweight': 'bold'})
    ax1.set_title('Lithology Distribution', fontsize=12, fontweight='bold', color='#1a5276')

    pct_values = [float(p.strip('%')) for p in lith_summary['Percentage']]
    ax2.bar(range(len(lith_summary)), pct_values, color=lith_colors)
    ax2.set_xticks(range(len(lith_summary)))
    ax2.set_xticklabels(lith_summary['Lithology'], rotation=45, ha='right', fontsize=9)
    ax2.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')
    ax2.set_title('Percentage Breakdown', fontsize=12, fontweight='bold', color='#1a5276')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    chart_path2 = f"{output_dir}/lithology_chart.png"
    plt.savefig(chart_path2, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    story.append(Image(chart_path2, width=6.5*inch, height=3*inch))
    story.append(PageBreak())

    # ==================== PAGE 4: COAL QUALITY ====================
    story.append(Paragraph("COAL SEAM QUALITY RANKING", heading_style))
    story.append(Spacer(1, 0.15*inch))

    seam_display = pd.concat([seam_quality.head(5), seam_quality.tail(10)])
    quality_data = [['Seam Name', 'CVAR', 'TM (%)', 'TS (%)', 'ASH (%)']]
    for _, row in seam_display.iterrows():
        quality_data.append([row['Seam_Name'], f"{row['Average_CVAR']:,.2f}",
                           f"{row['Average_TM (%)']:.2f}", f"{row['Average_TS (%)']:.2f}",
                           f"{row['Average_ASH (%)']:.2f}"])
    quality_data.insert(6, ['...', '...', '...', '...', '...'])

    quality_table = Table(quality_data, colWidths=[1.5*inch, 1.3*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    quality_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf2f8')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 1), (-1, 5), colors.HexColor('#fadbd8')),
        ('BACKGROUND', (0, 7), (-1, -1), colors.HexColor('#d5f5e3')),
        ('TEXTCOLOR', (0, 6), (-1, 6), colors.grey),
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
    ]))
    story.append(quality_table)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<i>Top 5 (red) = Lowest CVAR | Bottom 10 (green) = Highest CVAR</i>", 
                          ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.15*inch))

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor('white')
    colors_cvar = ['#e74c3c' if v < 5500 else '#f39c12' if v < 6500 else '#27ae60' for v in seam_quality['Average_CVAR']]
    ax.barh(range(len(seam_quality)), seam_quality['Average_CVAR'], color=colors_cvar)
    ax.set_yticks(range(len(seam_quality)))
    ax.set_yticklabels(seam_quality['Seam_Name'], fontsize=8)
    ax.set_xlabel('Average CVAR (kcal/kg)', fontsize=10, fontweight='bold')
    ax.set_title('Coal Seam Quality by CVAR', fontsize=12, fontweight='bold', color='#1a5276')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.axvline(x=5500, color='#e74c3c', linestyle='--', alpha=0.7)
    ax.axvline(x=6500, color='#27ae60', linestyle='--', alpha=0.7)

    plt.tight_layout()
    chart_path3 = f"{output_dir}/cvar_ranking_chart.png"
    plt.savefig(chart_path3, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    story.append(Image(chart_path3, width=6.5*inch, height=3*inch))
    story.append(PageBreak())

    # ==================== PAGE 5: SEAM THICKNESS ====================
    story.append(Paragraph("COAL SEAM THICKNESS SUMMARY", heading_style))
    story.append(Spacer(1, 0.15*inch))

    seam_agg = seam_thickness.groupby('Seam_Name').agg({
        'CalcThick': ['sum', 'mean', 'count'],
        'RIG': lambda x: ', '.join(sorted(x.unique()))
    }).reset_index()
    seam_agg.columns = ['Seam_Name', 'Total_Thickness', 'Avg_Thickness', 'Occurrences', 'Rigs_Present']
    seam_agg = seam_agg.sort_values('Total_Thickness', ascending=False).head(15)

    thickness_data = [['Seam Name', 'Total (m)', 'Avg (m)', 'Count', 'Rigs']]
    for _, row in seam_agg.iterrows():
        rigs_short = row['Rigs_Present'][:20] + '...' if len(row['Rigs_Present']) > 20 else row['Rigs_Present']
        thickness_data.append([row['Seam_Name'], f"{row['Total_Thickness']:.2f}",
                             f"{row['Avg_Thickness']:.2f}", f"{int(row['Occurrences'])}", rigs_short])

    thickness_table = Table(thickness_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1*inch, 1.8*inch])
    thickness_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf2f8')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(thickness_table)
    story.append(Spacer(1, 0.2*inch))

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('white')
    colors_thick = plt.cm.Blues(np.linspace(0.4, 0.9, len(seam_agg)))[::-1]
    ax.bar(range(len(seam_agg)), seam_agg['Total_Thickness'], color=colors_thick)
    ax.set_xticks(range(len(seam_agg)))
    ax.set_xticklabels(seam_agg['Seam_Name'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Total Thickness (m)', fontsize=10, fontweight='bold')
    ax.set_title('Top 15 Coal Seams by Thickness', fontsize=12, fontweight='bold', color='#1a5276')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    chart_path4 = f"{output_dir}/seam_thickness_chart.png"
    plt.savefig(chart_path4, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    story.append(Image(chart_path4, width=6.5*inch, height=2.8*inch))
    story.append(PageBreak())

    # ==================== PAGE 6: QUALITY PARAMS ====================
    story.append(Paragraph("COAL QUALITY PARAMETERS", heading_style))
    story.append(Spacer(1, 0.15*inch))

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    fig.patch.set_facecolor('white')

    ax = axes[0, 0]
    ax.scatter(seam_quality['Average_TM (%)'], seam_quality['Average_CVAR'],
             c=seam_quality['Average_CVAR'], cmap='RdYlGn', s=100, edgecolors='black')
    ax.set_xlabel('Total Moisture (%)', fontweight='bold')
    ax.set_ylabel('CVAR', fontweight='bold')
    ax.set_title('CVAR vs Moisture', fontweight='bold', color='#1a5276')
    ax.grid(alpha=0.3, linestyle='--')

    ax = axes[0, 1]
    ax.scatter(seam_quality['Average_ASH (%)'], seam_quality['Average_CVAR'],
             c=seam_quality['Average_CVAR'], cmap='RdYlGn', s=100, edgecolors='black')
    ax.set_xlabel('Ash Content (%)', fontweight='bold')
    ax.set_ylabel('CVAR', fontweight='bold')
    ax.set_title('CVAR vs Ash', fontweight='bold', color='#1a5276')
    ax.grid(alpha=0.3, linestyle='--')

    ax = axes[1, 0]
    ax.scatter(seam_quality['Average_TS (%)'], seam_quality['Average_CVAR'],
             c=seam_quality['Average_CVAR'], cmap='RdYlGn', s=100, edgecolors='black')
    ax.set_xlabel('Total Sulfur (%)', fontweight='bold')
    ax.set_ylabel('CVAR', fontweight='bold')
    ax.set_title('CVAR vs Sulfur', fontweight='bold', color='#1a5276')
    ax.grid(alpha=0.3, linestyle='--')

    ax = axes[1, 1]
    quality_class = []
    for _, row in seam_quality.iterrows():
        if row['Average_CVAR'] >= 6500 and row['Average_ASH (%)'] < 15:
            quality_class.append('Premium')
        elif row['Average_CVAR'] >= 5500:
            quality_class.append('Standard')
        else:
            quality_class.append('Low')
    class_counts = pd.Series(quality_class).value_counts()
    colors_class = ['#27ae60', '#f39c12', '#e74c3c']
    ax.pie(class_counts.values, labels=class_counts.index, autopct='%1.0f%%',
           colors=colors_class, textprops={'fontweight': 'bold'})
    ax.set_title('Quality Classification', fontweight='bold', color='#1a5276')

    plt.tight_layout()
    chart_path5 = f"{output_dir}/quality_params_chart.png"
    plt.savefig(chart_path5, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    story.append(Image(chart_path5, width=6.5*inch, height=4.5*inch))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("<b>Classification:</b> Premium (CVAR≥6500, Ash&lt;15%) | Standard (CVAR≥5500) | Low (CVAR&lt;5500)", body_style))
    story.append(PageBreak())

    # ==================== PAGE 7: CONCLUSIONS ====================
    story.append(Paragraph("DAILY OPERATIONS SUMMARY", heading_style))
    story.append(Paragraph("OPERATIONAL HIGHLIGHTS", subheading_style))

    highlights = [
        f"<b>Total Depth:</b> {total_depth:,.2f} meters across {total_rigs} rigs (avg {avg_depth_per_rig:,.2f}m/rig).",
        f"<b>Coal Discovery:</b> {total_coal_intervals} coal intervals across {unique_seams} distinct seams.",
        f"<b>Geology:</b> {len(lith_summary)} lithology types, {lith_summary.iloc[0]['Lithology']} most prevalent at {lith_summary.iloc[0]['Percentage']}.",
        f"<b>Quality Range:</b> CVAR {seam_quality.iloc[0]['Average_CVAR']:,.2f} to {seam_quality.iloc[-1]['Average_CVAR']:,.2f}.",
    ]
    for hl in highlights:
        story.append(Paragraph(hl, body_style))
        story.append(Spacer(1, 0.08*inch))

    story.append(Paragraph("RECOMMENDATIONS", subheading_style))
    recs = [
        f"<b>Priority:</b> Focus on {seam_quality.iloc[-1]['Seam_Name']} and {seam_quality.iloc[-2]['Seam_Name']} (highest CVAR).",
        f"<b>Efficiency:</b> Review {rig_totals.iloc[0]['RIG']} practices for fleet implementation.",
        f"<b>Quality:</b> Consider blending for {seam_quality.iloc[0]['Seam_Name']} (lowest CVAR).",
    ]
    for rec in recs:
        story.append(Paragraph(rec, body_style))
        story.append(Spacer(1, 0.08*inch))

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("— END OF REPORT —", ParagraphStyle('End', parent=styles['Normal'], 
                      alignment=TA_CENTER, fontSize=12, textColor=colors.grey, spaceBefore=20)))
    story.append(Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                      ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, 
                                    fontSize=8, textColor=colors.grey)))

    # Build PDF
    doc.build(story)
    print(f"✅ Report generated: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    create_daily_drilling_report()

print("Daily drilling report generation complete!" \
      "\nCheck the output folder for the generated PDF report.")