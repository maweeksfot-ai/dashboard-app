import streamlit as st
import json
from streamlit_lottie import st_lottie
import sys
import os
import pandas as pd
import numpy as np 
import requests
from io import BytesIO
from datetime import datetime

sys.path.append(os.path.join(os.getcwd(), "..", "data"))

st.set_page_config(page_title="Dewatering Dashboard", layout="wide")

live_urls = [ "https://1drv.ms/x/c/d6aca2526f83594b/IQAMcIopdLU9SINiVRsgBHwWAZsXQJ5-PHSv1BevGvZ8f0Q?download=1",
              "https://1drv.ms/x/c/d6aca2526f83594b/IQAlE6FfCDS_QL0HXfdxWdtCAae3Ilx-a_K9hA_PXGN3Ofs?download=1"
               ]

columns1 = ['Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']
columns2 = ['Date', 'Time','GPM_25', 'TOTAL_GAL_25', 'GPM_26','TOTAL_GAL_26','GPM_27', 'TOTAL_GAL_27', 'GPM_28','TOTAL_GAL_28', 'GPM_29', 'TOTAL_GAL_29', 'GPM_30','TOTAL_GAL_30', 'GPM_31', 'TOTAL_GAL_31', 'GPM_32', 'TOTAL_GAL_32', 'GPM_33','TOTAL_GAL_33', 'GPM_34', 'TOTAL_GAL_34', 'GPM_35', 'TOTAL_GAL_35', 'GPM_36','TOTAL_GAL_36', 'GPM_37', 'TOTAL_GAL_37', 'GPM_38', 'TOTAL_GAL_38', 'GPM_39','TOTAL_GAL_39', 'GPM_40', 'TOTAL_GAL_40', 'GPM_41', 'TOTAL_GAL_41','GPM_42', 'TOTAL_GAL_42', 'GPM_43', 'TOTAL_GAL_43', 'GPM_44','TOTAL_GAL_44', 'GPM_45', 'TOTAL_GAL_45', 'GPM_101', 'TOTAL_GAL_101','GPM_102', 'TOTAL_GAL_102', 'GPM_103', 'TOTAL_GAL_103', 'GPM_104','TOTAL_GAL_104', 'GPM_105', 'TOTAL_GAL_105', 'GPM_106', 'TOTAL_GAL_106','GPM_107', 'TOTAL_GAL_107', 'comments', 'datetime']

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

@st.cache_data()
def merge_and_sort(df1, df2):
    df_merged = pd.merge(df1, df2, on='datetime', how='outer', suffixes=('_1', '_2'))
    df_merged.sort_values('datetime', inplace=True)
    df_merged.reset_index(drop=True, inplace=True)
    df_merged = df_merged.drop(columns=['comments_1', 'comments_2'], errors='ignore')
    return df_merged

@st.cache_data()
def make_tidy(df):

    value_cols = [col for col in df.columns if 'GPM_' in col or 'TOTAL_GAL_' in col]

    df_long = df.melt(
        id_vars='datetime',
        value_vars=value_cols,
        var_name='variable',
        value_name='value'
    )
    df_long[['metric', 'pump']] = df_long['variable'].str.extract(r'(GPM|TOTAL_GAL)_(\d+)')
    df_long['pump'] = df_long['pump'].astype(int)
    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
    df_long.loc[(df_long['metric'] == 'GPM') & (df_long['value'] < 1),'value'] = 0
    # pivot
    df_tidy = df_long.pivot_table(
        index=['datetime', 'pump'],
        columns='metric',
        values='value'
    ).reset_index()
    df_tidy.columns.name = None
    return df_tidy

@st.cache_data()
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

@st.cache_data()
def get_daily_volume(df_tidy):
    df_tidy['date'] = df_tidy['datetime'].dt.date
    daily_total = (
        df_tidy.groupby(['date', 'pump'])['TOTAL_GAL']
        .agg(day_start='first', day_end='last')
        .reset_index()
    )
    daily_total['daily_volume'] = (daily_total['day_end'] - daily_total['day_start']).clip(lower=0)
    return daily_total

@st.cache_data()
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

def load_lottie_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def get_status(gpm):
    if gpm is None:
        return "NO DATA", "gray"
    elif gpm == 0:
        return "OFF", "red"
    elif gpm < 10:
        return "LOW", "orange"
    else:
        return "NORMAL", "blue"

def get_total_gallons(df):
    total = df.groupby('pump', as_index=False)['TOTAL_GAL'].max().round(1).sum()['TOTAL_GAL']
    return total 

def get_container_stats(df):
    date = list(df.loc[df.groupby('pump')['datetime'].idxmax()]['datetime'])
    pump_id = list(df.loc[df.groupby('pump')['datetime'].idxmax()]['pump'])
    gpm = list(df.loc[df.groupby('pump')['datetime'].idxmax()]['GPM'])
    total = list(df.loc[df.groupby('pump')['datetime'].idxmax()]['TOTAL_GAL'])
    return date, pump_id, gpm, total
@st.cache_data
def get_latest_per_pump(df):
    # get latest row per pump
    latest_df = df.loc[df.groupby('pump')['datetime'].idxmax()].reset_index(drop=True)
    return latest_df

@st.cache_data
def get_avg_gpm(df):
    avg = df.groupby(['pump'])['GPM'].mean().reset_index().round(1)
    return avg

@st.cache_data
def get_animation():
    return load_lottie_file("assets/water.json")

@st.cache_data
def load_lottie():
    import json
    with open("assets/water.json", "r") as f:
        return json.load(f)

def run_action():
    st.session_state.button_clicked = True

def main():
    st.markdown("<br>", unsafe_allow_html=True)

    st.set_page_config(page_title="Dewatering Dashboard", layout="wide")

    live_urls = [ "https://1drv.ms/x/c/d6aca2526f83594b/IQAMcIopdLU9SINiVRsgBHwWAZsXQJ5-PHSv1BevGvZ8f0Q?download=1",
                "https://1drv.ms/x/c/d6aca2526f83594b/IQAlE6FfCDS_QL0HXfdxWdtCAae3Ilx-a_K9hA_PXGN3Ofs?download=1"
                ]

    columns1 = ['Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']
    columns2 = ['Date', 'Time','GPM_25', 'TOTAL_GAL_25', 'GPM_26','TOTAL_GAL_26','GPM_27', 'TOTAL_GAL_27', 'GPM_28','TOTAL_GAL_28', 'GPM_29', 'TOTAL_GAL_29', 'GPM_30','TOTAL_GAL_30', 'GPM_31', 'TOTAL_GAL_31', 'GPM_32', 'TOTAL_GAL_32', 'GPM_33','TOTAL_GAL_33', 'GPM_34', 'TOTAL_GAL_34', 'GPM_35', 'TOTAL_GAL_35', 'GPM_36','TOTAL_GAL_36', 'GPM_37', 'TOTAL_GAL_37', 'GPM_38', 'TOTAL_GAL_38', 'GPM_39','TOTAL_GAL_39', 'GPM_40', 'TOTAL_GAL_40', 'GPM_41', 'TOTAL_GAL_41','GPM_42', 'TOTAL_GAL_42', 'GPM_43', 'TOTAL_GAL_43', 'GPM_44','TOTAL_GAL_44', 'GPM_45', 'TOTAL_GAL_45', 'GPM_101', 'TOTAL_GAL_101','GPM_102', 'TOTAL_GAL_102', 'GPM_103', 'TOTAL_GAL_103', 'GPM_104','TOTAL_GAL_104', 'GPM_105', 'TOTAL_GAL_105', 'GPM_106', 'TOTAL_GAL_106','GPM_107', 'TOTAL_GAL_107', 'comments', 'datetime']

    logo = ("assets/maweeks.png") 
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False

    if 'df_tidy' not in st.session_state:
        pass
        df1 = run_functions(live_urls[0], columns1)
        df2 = run_functions(live_urls[1], columns2)

        df_combined = merge_and_sort(df1, df2)
        df_tidy = make_tidy(df_combined)
        total_gallons = get_total_gallons(df_tidy)
        date, pump_id, gpm, total = get_container_stats(df_tidy) #switch these with get latest function eventually 

        latest = get_latest_per_pump(df_tidy)

        pump_list = latest['pump'].astype(str).tolist()
        gpm_list = latest['GPM'].astype(float).round(1).tolist()
        total_list = latest['TOTAL_GAL'].astype(float).tolist()
        date_list = latest['datetime'].dt.to_pydatetime().tolist()

        total_gpm = pd.Series(gpm).sum()  ## need to switch this with gpm list somehow .. 
        avg_gpms = get_avg_gpm(df_tidy)

        lottie_water = load_lottie()

    # Begin UI here
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.image(logo, width=120)  # Logo on left
    with col2:
        st.markdown("<h1 style='text-align: center;'>Deep Well Dashboard</h1>",unsafe_allow_html=True)
    with col3:
        st.write("")  # Empty column for spacing

    if st.button("🔄 Refresh Data", on_click=run_action):
        run_functions.clear()
        merge_and_sort.clear()
        make_tidy.clear()

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Site Flow", f"{total_gpm:.1f} gal/min")
    with col2:
        st.metric("Total Pumped", f"{total_gallons:,.0f} gal")
    with col3:
        st.metric("Last Reading", f"{date[0]}")
    st.header('Average GPMs')
    st.table(avg_gpms.set_index('pump').T.style.format("{:.1f}"))
    index = 0
    for i in range(13):  # 13 rows
        cols = st.columns(4)  # 4 columns
        
        for j in range(4):
            with cols[j]:
                with st.container(border=True):
                    st.subheader(f"DW {pump_list[index]}")
                    cur_gpm = gpm_list[index]
                    cur_total = total_list[index]
                    index += 1
                    status, color = get_status(cur_gpm) 
                    st.markdown(
                    f"<div style='height:6px;background:{color};border-radius:4px;'></div>",
                    unsafe_allow_html=True)
                    if status == "NO DATA":
                        st.info("⚪ No Data")
                    elif status == "OFF":
                        st.error("🔴 N/A")
                    elif status == "LOW":
                        st.warning("🟡 LOW FLOW")
                    else:
                        st.success("🔵 NORMAL")
                    if gpm is not None:
                        st_lottie(lottie_water, height=80)
                    st.metric("GPM", cur_gpm)
                    st.metric("Total", cur_total)

if __name__ == '__main__':
    main()






















