import sys
import os
import pandas as pd
import streamlit as st
from datetime import datetime, time
import altair as alt
from utils.data_pipeline import load_all_data
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")

sys.path.append(os.path.join(os.getcwd(), "..", "data"))

live_urls = [ "https://1drv.ms/x/c/d6aca2526f83594b/IQAMcIopdLU9SINiVRsgBHwWAZsXQJ5-PHSv1BevGvZ8f0Q?download=1",
              "https://1drv.ms/x/c/d6aca2526f83594b/IQAlE6FfCDS_QL0HXfdxWdtCAae3Ilx-a_K9hA_PXGN3Ofs?download=1"
               ]

columns1 = ['Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']
columns2 = ['Date', 'Time','GPM_25', 'TOTAL_GAL_25', 'GPM_26','TOTAL_GAL_26','GPM_27', 'TOTAL_GAL_27', 'GPM_28','TOTAL_GAL_28', 'GPM_29', 'TOTAL_GAL_29', 'GPM_30','TOTAL_GAL_30', 'GPM_31', 'TOTAL_GAL_31', 'GPM_32', 'TOTAL_GAL_32', 'GPM_33','TOTAL_GAL_33', 'GPM_34', 'TOTAL_GAL_34', 'GPM_35', 'TOTAL_GAL_35', 'GPM_36','TOTAL_GAL_36', 'GPM_37', 'TOTAL_GAL_37', 'GPM_38', 'TOTAL_GAL_38', 'GPM_39','TOTAL_GAL_39', 'GPM_40', 'TOTAL_GAL_40', 'GPM_41', 'TOTAL_GAL_41','GPM_42', 'TOTAL_GAL_42', 'GPM_43', 'TOTAL_GAL_43', 'GPM_44','TOTAL_GAL_44', 'GPM_45', 'TOTAL_GAL_45', 'GPM_101', 'TOTAL_GAL_101','GPM_102', 'TOTAL_GAL_102', 'GPM_103', 'TOTAL_GAL_103', 'GPM_104','TOTAL_GAL_104', 'GPM_105', 'TOTAL_GAL_105', 'GPM_106', 'TOTAL_GAL_106','GPM_107', 'TOTAL_GAL_107', 'comments', 'datetime']

if st.button("Refresh Data"):
    load_all_data.clear()

st.session_state.df_tidy, st.session_state.df_combined = load_all_data(
    live_urls, columns1, columns2
)

df_tidy = st.session_state.df_tidy
df_combined = st.session_state.df_combined


# Get all pumps
pump_options = sorted(df_tidy['pump'].unique().tolist())

# User selects pumps to analyze
selected_pumps = st.multiselect(
    "Select Pumps to Analyze",
    options=pump_options,
    default=pump_options[0]  # All selected by default
)

# Filter dataframe based on selection
df_selected = df_tidy[df_tidy['pump'].isin(selected_pumps)].copy()

def pump_health_summary(df, pumps=pump_options, freq_minutes=5):
    df = df.copy()
    
    if pumps is not None:
        df = df[df['pump'].isin(pumps)]
    # --- Ensure proper types ---
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['GPM'] = pd.to_numeric(df['GPM'], errors='coerce')
    df['TOTAL_GAL'] = pd.to_numeric(df['TOTAL_GAL'], errors='coerce')

    # --- Sort for time-based calculations ---
    df = df.sort_values(['pump', 'datetime'])

    # --- Volume between readings ---
    df['volume'] = df.groupby('pump')['TOTAL_GAL'].diff()

    # --- Running state ---
    df['is_running'] = df['GPM'] > 0

    # --- Time delta in hours ---
    df['dt_hours'] = df.groupby('pump')['datetime'].diff().dt.total_seconds() / 3600

    # fallback if evenly sampled
    df['dt_hours'] = df['dt_hours'].fillna(freq_minutes / 60)

    # --- Runtime hours ---
    df['runtime_hours'] = df['is_running'] * df['dt_hours']

    # --- Starts (on transitions) ---
    df['state_change'] = df.groupby('pump')['is_running'].diff().fillna(0)
    df['start'] = df['state_change'] == 1

    # --- Aggregate per pump ---
    summary = df.groupby('pump').agg(
        total_gallons=('TOTAL_GAL', lambda x: x.max() - x.min()),
        avg_gpm=('GPM', 'mean'),
        max_gpm=('GPM', 'max'),
        min_gpm=('GPM', lambda x: x[x > 0].min() if (x > 0).any() else 0),
        gpm_std=('GPM', 'std'),
        runtime_hours=('runtime_hours', 'sum'),
        total_hours=('dt_hours', 'sum'),
        starts=('start', 'sum'),
        data_points=('GPM', 'count')
    ).reset_index()

    # --- Derived metrics ---
    summary['duty_cycle'] = summary['runtime_hours'] / summary['total_hours']
    summary['gpm_cv'] = summary['gpm_std'] / summary['avg_gpm']
    summary['gal_per_hour'] = summary['total_gallons'] / summary['runtime_hours']

    # --- Handle divide-by-zero safely ---
    summary.replace([np.inf, -np.inf], np.nan, inplace=True)

    # --- Optional: round for display ---
    summary = summary.round({
        'avg_gpm': 1,
        'max_gpm': 1,
        'min_gpm': 1,
        'gpm_std': 2,
        'gpm_cv': 2,
        'runtime_hours': 1,
        'total_hours': 1,
        'duty_cycle': 2,
        'gal_per_hour': 1
    })

    return summary

def pump_anomalies(df, pumps=None):
    df = df.copy()
    if pumps is not None:
        df = df[df['pump'].isin(pumps)]
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(['pump','datetime'])
    df['volume'] = df.groupby('pump')['TOTAL_GAL'].diff()
    
    anomalies = df.groupby('pump').agg(
        negative_resets=('volume', lambda x: (x < 0).sum()),
        zero_flow_points=('GPM', lambda x: (x == 0).sum()),
        spike_count=('GPM', lambda x: (x > (x.mean() + 3*x.std())).sum()),
        data_points=('GPM','count')
    ).reset_index()
    
    # Percentages for interpretability
    anomalies['pct_negative_resets'] = anomalies['negative_resets'] / anomalies['data_points'] * 100
    anomalies['pct_zero_flow'] = anomalies['zero_flow_points'] / anomalies['data_points'] * 100
    anomalies['pct_spikes'] = anomalies['spike_count'] / anomalies['data_points'] * 100
    
    return anomalies

def pump_time_patterns(df, pumps=None):
    df = df.copy()
    if pumps is not None:
        df = df[df['pump'].isin(pumps)]
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Hour-of-day
    df['hour'] = df['datetime'].dt.hour
    hourly = df.groupby(['pump','hour'])['GPM'].mean().reset_index()
    
    # Day-of-week
    df['day'] = df['datetime'].dt.day_name()
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    df['day'] = pd.Categorical(df['day'], categories=day_order, ordered=True)
    daily = df.groupby(['pump','day'])['GPM'].mean().reset_index()
    
    return hourly, daily


summary = pump_health_summary(df_tidy)
anomalies = pump_anomalies(df_tidy)
hourly, daily = pump_time_patterns(df_tidy)

# --- Hour-of-Day Pattern ---
st.subheader("Average GPM by Hour")
hourly, daily = pump_time_patterns(df_selected, pumps=selected_pumps)

chart_hour = alt.Chart(hourly).mark_line(point=True).encode(
    x='hour:O',
    y='GPM:Q',
    color='pump:N',
    tooltip=['pump','hour','GPM']
).properties(width=700, height=400)
st.altair_chart(chart_hour, use_container_width=True)

# --- Day-of-Week Pattern ---
st.subheader("Average GPM by Day")
chart_day = alt.Chart(daily).mark_bar().encode(
    x='day:O',
    y='GPM:Q',
    color='pump:N',
    tooltip=['pump','day','GPM']
).properties(width=700, height=400)
st.altair_chart(chart_day, use_container_width=True)


st.subheader("Pump Health Summary")
st.dataframe(summary)

st.subheader("Anomalies")
st.dataframe(anomalies)

anomaly_summary = anomalies.copy()
anomaly_summary['pct_negative_resets'] = anomaly_summary['negative_resets'] / anomaly_summary['data_points'] * 100
anomaly_summary['pct_zero_flow'] = anomaly_summary['zero_flow_points'] / anomaly_summary['data_points'] * 100
anomaly_summary['pct_spikes'] = anomaly_summary['spike_count'] / anomaly_summary['data_points'] * 100


# st.subheader("Pump Anomalies Overview")

# for i, row in anomaly_summary.iterrows():
#     st.write(f"**Pump {row['pump']}**")
#     st.progress(min(row['pct_zero_flow'], 100))  # zero flows
#     st.progress(min(row['pct_spikes'], 100))    # spikes


df_anom = df_tidy.copy()
df_anom['volume'] = df_anom.groupby('pump')['TOTAL_GAL'].diff()
df_anom['spike'] = df_anom['GPM'] > (df_anom['GPM'].mean() + 3*df_anom['GPM'].std())
df_anom['zero_flow'] = df_anom['GPM'] == 0
df_anom['negative_reset'] = df_anom['volume'] < 0

import altair as alt

chart = alt.Chart(df_anom).mark_point(filled=True, size=80).encode(
    x='datetime:T',
    y='pump:N',
    color=alt.condition(
        alt.datum.spike | alt.datum.zero_flow | alt.datum.negative_reset,
        alt.value('red'),
        alt.value('green')
    ),
    tooltip=['pump', 'datetime', 'GPM', 'TOTAL_GAL']
).properties(title="Pump Anomalies Timeline")

st.altair_chart(chart, use_container_width=True)


heatmap = df_anom.groupby([df_anom['datetime'].dt.hour, 'pump'])['spike'].sum().reset_index()


st.subheader("Average GPM by Day of Week")

# Ensure days are in order
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily['day'] = pd.Categorical(daily['day'], categories=day_order, ordered=True)

chart_day = alt.Chart(daily).mark_bar().encode(
    x='day:O',
    y='GPM:Q',
    color='pump:N',
    tooltip=['pump', 'day', 'GPM']
).properties(
    width=700,
    height=400,
    title="Average GPM per Day for Each Pump"
)

st.altair_chart(chart_day, use_container_width=True)

hourly['GPM_smooth'] = hourly.groupby('pump')['GPM'].rolling(3).mean().reset_index(0, drop=True)



import seaborn as sns
import matplotlib.pyplot as plt

heatmap_data = df_tidy.copy()
heatmap_data['hour'] = heatmap_data['datetime'].dt.hour
heatmap_data['day'] = heatmap_data['datetime'].dt.day_name()

pivot = heatmap_data.pivot_table(index='hour', columns='day', values='GPM', aggfunc='mean')
sns.heatmap(pivot[day_order])
plt.title("Pump GPM Heatmap by Hour & Day")
st.pyplot(plt)


