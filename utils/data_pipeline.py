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
def load_all_data(live_urls, columns1, columns2):
    df1 = run_functions(live_urls[0], columns1)
    df2 = run_functions(live_urls[1], columns2)
    df_combined = merge_and_sort(df1, df2)
    df_tidy = make_tidy(df_combined)

    return df_tidy