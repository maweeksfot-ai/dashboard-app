import sys
import os
import requests
import pandas as pd
from io import BytesIO
from datetime import datetime, time
import streamlit as st

url = "https://1drv.ms/x/c/d6aca2526f83594b/IQAc8ap_zmWhR5goYf70_b69AU0CyhmpxFroY48j8pNaZac?download=1"


columns = ['date',	'time', 'TOW_1','TOW_2','TOW_3', 'TOW_4', 'TOW_5', 'TOW_6', 'TOW_7', 'TOW_8', 'TOW_15'	,'TOW_16','TOW_17','TOW_18', 'comments']
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

def get_data(url):
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
    return df

def shape_df(df):
    # cut the first 5 rows and first column 
    df = df.iloc[25:,2:].reset_index(drop=True)
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
    mask = df['time'].apply(lambda x: isinstance(x, datetime))
    df.loc[mask, 'time'] = df.loc[mask, 'time'].apply(lambda x: x.time())
    return df

def make_datetime_col(df):
    df['datetime'] = df.apply(
        lambda row: datetime.combine(row['date'].date(), row['time']),
        axis=1
    )
    return df

def fix_space(df):
    df.columns = df.columns.str.replace('.', '_', regex=False)
    df.columns = df.columns.str.replace(' ', '_', regex=False)  # replace spaces
    return df

def drop_DT(df):
    # strip all columns with "Unnamed" string
    df = df.drop(columns=['date', 'time'], errors='ignore')
    return df

def make_tidy(df):

    value_cols = [col for col in df.columns if 'TOW_' in col ]

    df_long = df.melt(
        id_vars='datetime',
        value_vars=value_cols,
        var_name='tow',
        value_name='value'
    )
    
    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
    df_long['tow'] = (df_long['tow'].str.replace('TOW_', '', regex=False).astype(int))

    df_long.columns.name = None
    return df_long


def make_tidy_with_phases(df, phase_1, phase_2, toc):
    # 🔑 ضمان correct order
    value_cols = sorted(
        [col for col in df.columns if 'TOW_' in col],
        key=lambda x: int(x.replace('TOW_', ''))
    )

    df_long = df.melt(
        id_vars=[col for col in df.columns if col not in value_cols],
        value_vars=value_cols,
        var_name='tow',
        value_name='value'
    )

    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')

    # Map index based on correct column order
    col_index_map = {col: i for i, col in enumerate(value_cols)}
    df_long['idx'] = df_long['tow'].map(col_index_map)

    df_long['phase_1'] = df_long['idx'].map(lambda i: phase_1[i] if i < len(phase_1) else None)
    df_long['phase_2'] = df_long['idx'].map(lambda i: phase_2[i] if i < len(phase_2) else None)
    df_long['toc'] = df_long['idx'].map(lambda i: toc[i] if i < len(toc) else None)

    df_long['tow'] = df_long['tow'].str.replace('TOW_', '', regex=False).astype(int)
    df_long = df_long.drop(columns='idx')

    # Force numeric
    for col in ['phase_1', 'phase_2', 'toc']:
        df_long[col] = pd.to_numeric(df_long[col], errors='coerce')

    df_long.columns.name = None
    return df_long

@st.cache_data()
def run_functions(url=url, col=columns):
    df = get_data(url)
    df = shape_df(df)
    df = trim_frame(df, col)
    df = clean_col(df)
    df = fix_time(df)
    df = make_datetime_col(df)
    df = fix_space(df)
    df_wide = drop_DT(df)
    df_long = make_tidy(df)
    # df_long = make_tidy_with_phases(df, phase_1, phase_2, toc)

    return df_long, df_wide 


tow_df, df_wide = run_functions()

