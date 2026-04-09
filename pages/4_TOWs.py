import sys
import os
import pandas as pd
import streamlit as st
from datetime import datetime, time
import altair as alt
from utils.tow_pipeline import run_functions
import numpy as np
import re
st.set_page_config(layout="wide")

sys.path.append(os.path.join(os.getcwd(), "..", "data"))


phase_1 = 4568
phase_2 = 4543

toc_elev = {
    'TOW_1': 4572.92,
    'TOW_2': 4571.70,
    'TOW_3': 4572.80,
    'TOW_4': 4574.58,
    'TOW_5': 4572.98,
    'TOW_6': 4573.53,
    'TOW_7': 4573.30,
    'TOW_8': 4569.75,
    'TOW_15': 4589.30,
    'TOW_16': 4580.34,
    'TOW_17': 4581.15,
    'TOW_18': 4586.93
}
cur_elev = {
    'TOW_1': 0,
    'TOW_2': 0,
    'TOW_3': 0,
    'TOW_4': 0,
    'TOW_5': 0,
    'TOW_6': 0,
    'TOW_7': 0,
    'TOW_8': 0,
    'TOW_15': 0,
    'TOW_16': 0,
    'TOW_17': 0,
    'TOW_18': 0
}


if st.button("Refresh Data"):
    run_functions.clear()

st.session_state.df_long, st.session_state.df_wide  = run_functions()

df_long = st.session_state.df_long
df_wide = st.session_state.df_wide

st.header("TOW Analytics")


df_long['datetime'] = pd.to_datetime(df_long['datetime'])
df_wide['datetime'] = pd.to_datetime(df_long['datetime'])

st.header("TOW Levels")
tow = st.selectbox('Select TOW', sorted(df_long['tow'].unique()))
filtered = df_long[df_long['tow'] == tow]
st.line_chart(filtered.set_index('datetime')['value'])


st.header("TOW Comparison")
# Example: resample to hourly means
df_slim = df_long.set_index('datetime').groupby('tow', group_keys=False).resample('1D').mean().reset_index()
tows = sorted(df_slim['tow'].unique())
tow_options = tows
selected_tows = st.multiselect("Select TOWS", tow_options, default=[tow_options[0]])

filtered_tows = df_slim[df_slim['tow'].isin(selected_tows)]
line_chart = alt.Chart(filtered_tows).mark_line(point=True).encode(
    x='datetime:T',
    y='value:Q',
    color='tow:N',
    tooltip=['tow', 'datetime']
).interactive()

st.altair_chart(line_chart, width='stretch')


# df_long['current_elevation'] = df_long['tow'].map(toc_elev) - df_long['value']

depth = ((df_long[df_long['value'].notna()]).sort_values('datetime').groupby('tow', as_index=False).last())

depth = depth.set_index('tow')
x = list(depth['value'])

index = 0
for k in toc_elev.keys():
    top = toc_elev[k]
    drop = (x[index])
    cur_elev[k] = (top - drop)
    index += 1
cur_elev = {k: round(v, 2) for k, v in cur_elev.items()}

# st.write(cur_elev)

# --- Prepare DataFrame ---
df = pd.DataFrame(list(cur_elev.items()), columns=['Label', 'TOW'])

# Extract numeric part of TOW label for sorting
df['TOW_Num'] = df['Label'].apply(lambda x: int(re.search(r'\d+', x).group()))
df = df.sort_values('TOW_Num')

# Thresholds
phase_1 = 4568
phase_2 = 4543

# Add status columns
df['Phase_1_Status'] = df['TOW'].apply(lambda x: 'Above' if x > phase_1 else 'Below')
df['Phase_2_Status'] = df['TOW'].apply(lambda x: 'Above' if x > phase_2 else 'Below')

# Determine min/max for zoomed y-axis
y_min = df['TOW'].min() - 5
y_max = df['TOW'].max() + 5

# Base chart
base = alt.Chart(df).encode(
    x=alt.X('Label:N', title='TOW Label', sort=df['Label'].tolist()),  # sorted numerically
    y=alt.Y('TOW:Q', title='TOW Value', scale=alt.Scale(domain=[y_min, y_max]))
)

# Line chart with points colored by Phase 2 status
line = base.mark_line(point=True).encode(
    color=alt.condition(
        alt.datum.TOW > phase_2,
        alt.value('green'),
        alt.value('red')
    )
)

# Threshold lines
thresholds = alt.Chart(pd.DataFrame({
    'Phase': ['Phase 1', 'Phase 2'],
    'Value': [phase_1, phase_2]
})).mark_rule(strokeDash=[5,5]).encode(
    y='Value:Q',
    color='Phase:N'
)

# Combine
chart = line + thresholds
st.altair_chart(chart, use_container_width=True)

#### END OF TOW PHASE LOGIC

st.dataframe(df_wide.tail(12))



