import sys
import os
import requests
import pandas as pd
from io import BytesIO
import streamlit as st
from datetime import datetime, time


sys.path.append(os.path.join(os.getcwd(), "..", "data"))

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

def merge_and_sort(df1, df2):
    df_merged = pd.merge(df1, df2, on='datetime', how='outer', suffixes=('_1', '_2'))
    df_merged.sort_values('datetime', inplace=True)
    df_merged.reset_index(drop=True, inplace=True)
    df_merged = df_merged.drop(columns=['comments_1', 'comments_2'], errors='ignore')
    return df_merged

def run_functions(url, list):
    df = get_data(url)
    df = shape_df(df)
    df = trim_frame(df, list)  # df2 check too 
    df = clean_col(df)
    df = fix_time(df)
    df = make_datetime_col(df)
    df = fix_space(df)
    df = drop_DT(df)
    return df

df1 = run_functions(urls[0], col)
df2 = run_functions(urls[1], col2)

st.cache_data(ttl=3600)
df_combined = merge_and_sort(df1, df2)

st.dataframe(df_combined)
# loop to make columns and rows 

pump = st.selectbox("Select Pump", [1,2,3,4,5])  # expand later

st.line_chart(
    df_combined.set_index('datetime')[f'GPM_{pump}']
)


# # gpm_cols = [col for col in df_combined.columns if 'GPM_' in col]

# # df_combined['total_GPM'] = df_combined[gpm_cols].sum(axis=1)

# # st.line_chart(df_combined.set_index('datetime')['total_GPM'])




# # df_combined['Pump1_running'] = df_combined['GPM_1'] > 0

# # runtime = df_combined['Pump1_running'].sum()
# # st.write(f"Pump 1 runtime (rows): {runtime}")




# # runtime_pct = (df_combined['GPM_1'] > 0).mean() * 100
# # st.write(f"Pump 1 runtime: {runtime_pct:.2f}%")







# df_daily = (
#     df_combined
#     .set_index('datetime')
#     .select_dtypes(include='number')
#     .resample('D')
#     .sum()
# )

# st.line_chart(df_daily['total_GPM'])






# pump_totals = {
#     col: df_combined[col].sum()
#     for col in df_combined.columns if 'GPM_' in col
# }

# st.bar_chart(pd.Series(pump_totals))





# #### spikes 
# threshold = df_combined['GPM_1'].mean() + 3 * df_combined['GPM_1'].std()

# spikes = df_combined[df_combined['GPM_1'] > threshold]

# st.write(spikes)





# # rate of change 
# df_combined['GPM_1_diff'] = df_combined['GPM_1'].diff()

# st.line_chart(df_combined.set_index('datetime')['GPM_1_diff'])

# for i in range(13):  # 13 rows
#     cols = st.columns(4)  # 4 columns
    
#     for j in range(4):
#         with cols[j]:
#             st.container().write(f"Row {i+1}, Col {j+1}")  # make this a function call


import pandas as pd
import streamlit as st

# =========================
# 🔹 CLEAN NUMERIC COLUMNS
# =========================
def clean_numeric(df):
    pump_cols = [col for col in df.columns if 'GPM_' in col or 'TOTAL_GAL_' in col]
    
    # Convert everything to numeric safely
    df[pump_cols] = df[pump_cols].apply(pd.to_numeric, errors='coerce')
    
    return df, pump_cols


# =========================
# 🔹 ADD TOTAL GPM
# =========================
def add_total_gpm(df, pump_cols):
    gpm_cols = [col for col in pump_cols if 'GPM_' in col]
    
    df['total_GPM'] = df[gpm_cols].sum(axis=1)
    
    return df


# =========================
# 🔹 DAILY AGGREGATION
# =========================
def get_daily(df):
    df_daily = (
        df
        .set_index('datetime')
        .select_dtypes(include='number')  # avoid string errors
        .resample('D')
        .sum()
    )
    return df_daily


# =========================
# 🔹 PUMP RUNTIME %
# =========================
def get_runtime(df, pump_cols):
    runtime = {}
    
    for col in pump_cols:
        if 'GPM_' in col:
            runtime[col] = (df[col] > 0).mean() * 100
    
    return pd.Series(runtime).sort_values(ascending=False)


# =========================
# 🔹 PUMP TOTAL USAGE
# =========================
def get_totals(df, pump_cols):
    totals = {}
    
    for col in pump_cols:
        if 'GPM_' in col:
            totals[col] = df[col].sum()
    
    return pd.Series(totals).sort_values(ascending=False)


# =========================
# 🔹 SPIKE DETECTION
# =========================
def get_spikes(df, pump_col):
    mean = df[pump_col].mean()
    std = df[pump_col].std()
    
    threshold = mean + 3 * std
    
    spikes = df[df[pump_col] > threshold]
    
    return spikes


# =========================
# 🔹 MAIN PIPELINE
# =========================
def run_analysis(df_combined):

    # Ensure datetime is correct
    df_combined['datetime'] = pd.to_datetime(df_combined['datetime'])

    # Clean numeric columns
    df_combined, pump_cols = clean_numeric(df_combined)

    # Fill NaNs (important since pumps come online at different times)
    df_combined[pump_cols] = df_combined[pump_cols].fillna(0)

    # Add total GPM
    df_combined = add_total_gpm(df_combined, pump_cols)

    # Daily aggregation
    df_daily = get_daily(df_combined)

    # Runtime + totals
    runtime = get_runtime(df_combined, pump_cols)
    totals = get_totals(df_combined, pump_cols)

    return df_combined, df_daily, runtime, totals


# =========================
# 🔹 STREAMLIT UI
# =========================
df_combined, df_daily, runtime, totals = run_analysis(df_combined)

st.title("Pump Dashboard")

# ---- Total System Flow ----
st.subheader("Total System GPM Over Time")
st.line_chart(df_combined.set_index('datetime')['total_GPM'])

# ---- Daily Total ----
st.subheader("Daily Total GPM")
st.line_chart(df_daily['total_GPM'])

# ---- Pump Selection ----
gpm_cols = [col for col in df_combined.columns if 'GPM_' in col]
pump = st.selectbox("Select Pump", gpm_cols)

st.subheader(f"{pump} Over Time")
st.line_chart(df_combined.set_index('datetime')[pump])

# ---- Runtime ----
st.subheader("Pump Runtime %")
st.bar_chart(runtime)

# ---- Total Usage ----
st.subheader("Pump Total Usage")
st.bar_chart(totals)

# ---- Spikes ----
st.subheader("Spike Detection")
spikes = get_spikes(df_combined, pump)
st.write(spikes)