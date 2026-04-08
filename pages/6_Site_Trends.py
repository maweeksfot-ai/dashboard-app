import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.tow_pipeline import run_functions
from utils.data_pipeline import load_all_data


# -----------------------------
# Load data once into session_state
# -----------------------------
if 'df_long' not in st.session_state or 'df_tidy' not in st.session_state:
    st.session_state.df_long, st.session_state.df_wide = run_functions()
    st.session_state.df_tidy, st.session_state.df_combined = load_all_data()

df_long = st.session_state.df_long
df_tidy = st.session_state.df_tidy

# Convert datetime only once
if 'datetime_converted' not in st.session_state:
    df_long['datetime'] = pd.to_datetime(df_long['datetime'])
    df_tidy['datetime'] = pd.to_datetime(df_tidy['datetime'])
    st.session_state.datetime_converted = True

# -----------------------------
# Weekly aggregation (store in session_state)
# -----------------------------
if 'weekly_tow' not in st.session_state:
    # Compute week column
    df_long['week'] = df_long['datetime'].dt.to_period('W').apply(lambda r: r.start_time)
    # TOW weekly mean
    st.session_state.weekly_tow = df_long.groupby(['tow', 'week'])['value'].mean().reset_index()

if 'weekly_pump' not in st.session_state:
    df_tidy['week'] = df_tidy['datetime'].dt.to_period('W').apply(lambda r: r.start_time)
    st.session_state.weekly_pump = df_tidy.groupby('week')['TOTAL_GAL'].sum().reset_index()

weekly_tow = st.session_state.weekly_tow.copy()
weekly_pump = st.session_state.weekly_pump.copy()

# -----------------------------
# Date range slider
# -----------------------------
min_date = max(df_long['datetime'].min(), df_tidy['datetime'].min()).date()
max_date = min(df_long['datetime'].max(), df_tidy['datetime'].max()).date()

start_date, end_date = st.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

start_ts = pd.Timestamp(start_date)
end_ts = pd.Timestamp(end_date)

# Filter weekly data by selected date
weekly_tow_filtered = weekly_tow[(weekly_tow['week'] >= start_ts) & (weekly_tow['week'] <= end_ts)]
weekly_pump_filtered = weekly_pump[(weekly_pump['week'] >= start_ts) & (weekly_pump['week'] <= end_ts)]

# -----------------------------
# Multiselect for TOWs
# -----------------------------
tow_options = weekly_tow_filtered['tow'].unique()
if 'selected_tows' not in st.session_state:
    st.session_state.selected_tows = list(tow_options)

selected_tows = st.multiselect(
    "Select TOWs to display",
    options=tow_options,
    default=st.session_state.selected_tows,
    key='tow_multiselect'
)
st.session_state.selected_tows = selected_tows

# Filter TOWs
weekly_tow_filtered = weekly_tow_filtered[weekly_tow_filtered['tow'].isin(selected_tows)]

# -----------------------------
# Plotly figure
# -----------------------------
fig = go.Figure()

# Add TOW lines
for tow_name in weekly_tow_filtered['tow'].unique():
    df_plot = weekly_tow_filtered[weekly_tow_filtered['tow'] == tow_name]
    fig.add_trace(go.Scatter(
        x=df_plot['week'],
        y=df_plot['value'],
        mode='lines+markers',
        name=f"{tow_name} TOW",
        yaxis='y1'
    ))

# Add Pump line
fig.add_trace(go.Scatter(
    x=weekly_pump_filtered['week'],
    y=weekly_pump_filtered['TOTAL_GAL'],
    mode='lines+markers',
    name='Total Pumped (Gal)',
    yaxis='y2',
    line=dict(color='red', width=3)
))

# Layout
fig.update_layout(
    title="Weekly TOW Levels vs Pumped Volume",
    xaxis_title="Week",
    yaxis=dict(title="Water Level (ft)", side='left'),
    yaxis2=dict(title="Total Pumped (Gal)", overlaying='y', side='right'),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

