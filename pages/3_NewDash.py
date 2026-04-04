import sys
import os
import requests
import pandas as pd
from io import BytesIO
import streamlit as st
from datetime import datetime, time
import altair as alt

st.set_page_config(layout="wide")

sys.path.append(os.path.join(os.getcwd(), "..", "data"))

live_urls = [ "https://1drv.ms/x/c/d6aca2526f83594b/IQAMcIopdLU9SINiVRsgBHwWAZsXQJ5-PHSv1BevGvZ8f0Q?download=1",
              "https://1drv.ms/x/c/d6aca2526f83594b/IQAlE6FfCDS_QL0HXfdxWdtCAae3Ilx-a_K9hA_PXGN3Ofs?download=1"
               ]

urls = [ "https://1drv.ms/x/c/f6261b79731e452c/IQBpBPUwwVtQTYrz4LgAWE6ZAfTxxxhud5AzyDm4tVY5P-0?download=1",   # Dirty 1 - 24
         "https://1drv.ms/x/c/f6261b79731e452c/IQDTm4wgClDgRKutu40S_fAUASzQrkvm2Z--Qe2whPBX1xI?download=1"
         ]   # Dirty 25 - 107 

col = ['Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']
col2 = ['Date', 'Time','GPM_25', 'TOTAL_GAL_25', 'GPM_26','TOTAL_GAL_26','GPM_27', 'TOTAL_GAL_27', 'GPM_28','TOTAL_GAL_28', 'GPM_29', 'TOTAL_GAL_29', 'GPM_30','TOTAL_GAL_30', 'GPM_31', 'TOTAL_GAL_31', 'GPM_32', 'TOTAL_GAL_32', 'GPM_33','TOTAL_GAL_33', 'GPM_34', 'TOTAL_GAL_34', 'GPM_35', 'TOTAL_GAL_35', 'GPM_36','TOTAL_GAL_36', 'GPM_37', 'TOTAL_GAL_37', 'GPM_38', 'TOTAL_GAL_38', 'GPM_39','TOTAL_GAL_39', 'GPM_40', 'TOTAL_GAL_40', 'GPM_41', 'TOTAL_GAL_41','GPM_42', 'TOTAL_GAL_42', 'GPM_43', 'TOTAL_GAL_43', 'GPM_44','TOTAL_GAL_44', 'GPM_45', 'TOTAL_GAL_45', 'GPM_101', 'TOTAL_GAL_101','GPM_102', 'TOTAL_GAL_102', 'GPM_103', 'TOTAL_GAL_103', 'GPM_104','TOTAL_GAL_104', 'GPM_105', 'TOTAL_GAL_105', 'GPM_106', 'TOTAL_GAL_106','GPM_107', 'TOTAL_GAL_107', 'comments', 'datetime']

st.cache_data(ttl=3600)
def get_data(url):
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
    return df

def shape_df(df):
    # cut the first 5 rows and first column 
    df = df.iloc[5:,1:].reset_index(drop=True)
    return df

def trim_frame(df, new_col):
    df = df.iloc[:, :len(new_col)] 
    df.columns = new_col
    return df

def clean_col(df):
    # strip all columns with "Unnamed" string
    for col in df.columns:
        if "Unnamed" in str(col):
            df = df.drop(columns=[str(col)], errors='ignore')
    return df

def fix_time(df):
    mask = df['Time'].apply(lambda x: isinstance(x, datetime))
    df.loc[mask, 'Time'] = df.loc[mask, 'Time'].apply(lambda x: x.time())
    return df

def make_datetime_col(df):
    df['datetime'] = df.apply(
        lambda row: datetime.combine(row['Date'].date(), row['Time']),
        axis=1
    )
    return df

def fix_space(df):
    df.columns = df.columns.str.replace('.', '_', regex=False)
    df.columns = df.columns.str.replace(' ', '_', regex=False)  # replace spaces
    return df

def drop_DT(df):
    # strip all columns with "Unnamed" string
    df = df.drop(columns=['Date', 'Time'], errors='ignore')
    return df

@st.cache_data(ttl=3600)
def merge_and_sort(df1, df2):
    df_merged = pd.merge(df1, df2, on='datetime', how='outer', suffixes=('_1', '_2'))
    df_merged.sort_values('datetime', inplace=True)
    df_merged.reset_index(drop=True, inplace=True)
    df_merged = df_merged.drop(columns=['comments_1', 'comments_2'], errors='ignore')
    return df_merged

@st.cache_data(ttl=3600)
def make_tidy(df):

    value_cols = [col for col in df.columns if 'GPM_' in col or 'TOTAL_GAL_' in col]

    df_long = df.melt(
        id_vars='datetime',
        value_vars=value_cols,
        var_name='variable',
        value_name='value'
    )

    # split column names
    df_long[['metric', 'pump']] = df_long['variable'].str.extract(r'(GPM|TOTAL_GAL)_(\d+)')
    df_long['pump'] = df_long['pump'].astype(int)

    # 🔑 FIX: force numeric
    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')

    # 🔑 apply rule: GPM < 1 → 0
    df_long.loc[(df_long['metric'] == 'GPM') & (df_long['value'] < 1),'value'] = 0
    # pivot
    df_tidy = df_long.pivot_table(
        index=['datetime', 'pump'],
        columns='metric',
        values='value'
    ).reset_index()
    df_tidy.columns.name = None
    return df_tidy

@st.cache_data(ttl=3600)
def run_functions(url, list):
    df = get_data(url)
    df = shape_df(df)
    df = trim_frame(df, list)  # df2 check too 
    df = clean_col(df)
    df = fix_time(df)
    df = make_datetime_col(df)
    df = fix_space(df)
    df = drop_DT(df)
    print("The functions ran ....")
    return df

@st.cache_data(ttl=3600)
def get_daily_volume(df_tidy):
    df_tidy['date'] = df_tidy['datetime'].dt.date
    daily_total = (
        df_tidy.groupby(['date', 'pump'])['TOTAL_GAL']
        .agg(day_start='first', day_end='last')
        .reset_index()
    )
    daily_total['daily_volume'] = (daily_total['day_end'] - daily_total['day_start']).clip(lower=0)
    return daily_total

@st.cache_data(ttl=3600)
def get_weekly_volume(df_tidy):
    # Ensure datetime is datetime type
    df_tidy['datetime'] = pd.to_datetime(df_tidy['datetime'])
    # Group by pump and week
    weekly_total = (
        df_tidy.groupby(['pump', pd.Grouper(key='datetime', freq='W')])['TOTAL_GAL']
        .agg(day_start='first', day_end='last')
        .reset_index()
    )
    # Actual pumped volume = last - first
    weekly_total['weekly_volume'] = (weekly_total['day_end'] - weekly_total['day_start']).clip(lower=0)
    return weekly_total
def main():

    df1 = run_functions(live_urls[0], col)
    df2 = run_functions(live_urls[1], col2)


    df_combined = merge_and_sort(df1, df2)
    df_tidy = make_tidy(df_combined)

    st.write(df_tidy.info())
    print(df_tidy.info())
    # st.dataframe(df_tidy)
    st.header("Total Gallons By Pump")
    pump = st.selectbox("Select Pump", sorted(df_tidy['pump'].unique()))
    filtered = df_tidy[df_tidy['pump'] == pump]
    st.line_chart(filtered.set_index('datetime')['TOTAL_GAL'])


    # calculate daily pumped volume from cumulative readings
    # ensure datetime is actually datetime type
    # make sure datetime
    df_tidy['datetime'] = pd.to_datetime(df_tidy['datetime'])
    df_tidy['date'] = df_tidy['datetime'].dt.date

    pump_id = 1  # choose the pump you want
    df_pump = df_tidy[df_tidy['pump'] == pump_id].copy()
    df_pump['datetime'] = pd.to_datetime(df_pump['datetime'])

    # Set datetime as index for resampling
    df_pump.set_index('datetime', inplace=True)

    # Resample by week, get first and last cumulative values
    weekly = df_pump['TOTAL_GAL'].resample('W').agg(['first', 'last'])
    # Actual pumped volume
    weekly['weekly_volume'] = (weekly['last'] - weekly['first']).clip(lower=0)
    weekly = weekly.reset_index()

    bar_chart = alt.Chart(weekly).mark_bar().encode(
        x='datetime:T',
        y='weekly_volume:Q',
        tooltip=['datetime', 'weekly_volume']
    )

    st.altair_chart(bar_chart, use_container_width=True)

    line_chart = alt.Chart(weekly).mark_line(point=True).encode(
        x='datetime:T',           # time on x-axis
        y='weekly_volume:Q',      # pumped volume on y-axis
        tooltip=['datetime', 'weekly_volume']).properties(title=f'Weekly Pumped Volume for Pump {pump_id}').interactive()  # allows zoom/pan

    st.altair_chart(line_chart, use_container_width=True)





    df_tidy['datetime'] = pd.to_datetime(df_tidy['datetime'])

    # Set datetime as index
    df_tidy_indexed = df_tidy.set_index('datetime')

    # Group by pump and resample weekly
    weekly = (
        df_tidy_indexed.groupby('pump')['TOTAL_GAL']
        .resample('W')  # weekly frequency
        .agg(first='first', last='last')
        .reset_index()  # bring 'pump' back as column
    )

    # Compute actual weekly pumped volume
    weekly['weekly_volume'] = (weekly['last'] - weekly['first']).clip(lower=0)


    pump_options = sorted(df_tidy['pump'].unique())
    selected_pumps = st.multiselect("Select Pumps", pump_options, default=[pump_options[0]])

    weekly_filtered = weekly[weekly['pump'].isin(selected_pumps)]

    line_chart = alt.Chart(weekly_filtered).mark_line(point=True).encode(
        x='datetime:T',
        y='weekly_volume:Q',
        color='pump:N',
        tooltip=['pump', 'datetime', 'weekly_volume']
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)
    # # =========================
    # # 🔹 STREAMLIT UI
    # # =========================
    # df_combined, df_daily, runtime, totals = run_analysis(df_combined)

    # st.title("Pump Dashboard")

    # # ---- Total System Flow ----
    # st.subheader("Total System GPM Over Time")
    # st.line_chart(df_combined.set_index('datetime')['total_GPM'])

    # # ---- Daily Total ----
    # st.subheader("Daily Total GPM")
    # st.line_chart(df_daily['total_GPM'])

    # # ---- Pump Selection ----
    # gpm_cols = [col for col in df_combined.columns if 'GPM_' in col]
    # pump = st.selectbox("Select Pump", gpm_cols)

    # st.subheader(f"{pump} Over Time")
    # st.line_chart(df_combined.set_index('datetime')[pump])

    # # ---- Runtime ----
    # st.subheader("Pump Runtime %")
    # st.bar_chart(runtime)

    # # ---- Total Usage ----
    # st.subheader("Pump Total Usage")
    # st.bar_chart(totals)

    # # ---- Spikes ----
    # st.subheader("Spike Detection")
    # spikes = get_spikes(df_combined, pump)
    # st.write(spikes)


main()
