import sys
import os
import pandas as pd
import streamlit as st
from datetime import datetime, time
import altair as alt
from utils.tow_pipeline import run_functions

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


if st.button("Refresh Data"):
    run_functions.clear()

st.session_state.df_long, st.session_state.df_wide  = run_functions()

df_long = st.session_state.df_long
df_wide = st.session_state.df_wide

st.header("TOW Analytics")



st.dataframe(df_long.tail())

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



st.dataframe(df_wide.tail(12))



