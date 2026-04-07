import sys
import os
import requests
import pandas as pd
import sqlite3
from io import BytesIO

#  https://1drv.ms/x/c/f6261b79731e452c/IQAWBwanD61xSKrJ_UcUYI4FAa-UyjOruqjXIwO12-5lKU4?download=1  # dw 1-24 cleaned 
#  https://1drv.ms/x/c/f6261b79731e452c/IQCf275GvfAtTq_xIZuNI9fmAU3J6I3ga_BZ1pox5YbWMD8?download=1  # dw 25-107 cleaned 

urls = [
    "https://1drv.ms/x/c/f6261b79731e452c/IQAWBwanD61xSKrJ_UcUYI4FAa-UyjOruqjXIwO12-5lKU4?download=1",
    "https://1drv.ms/x/c/f6261b79731e452c/IQBpBPUwwVtQTYrz4LgAWE6ZAfTxxxhud5AzyDm4tVY5P-0?download=1" # copy of live 1-24
]

# request data from onedrive URL and return dirty onedrive url

def get_data(url):
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
    return df

df1 = get_data(urls[0])
df2 = get_data(urls[1])



# begin cleaning new data frames
# cut the first 5 rows and first column 

df2 = df2.iloc[5:,1:].reset_index(drop=True)


# new_columns = ['Date', 'Time', 'GPM', 'TOTAL GAL', 'GPM.1', 'TOTAL GAL.1', 'GPM.2', 'TOTAL GAL.2', 'GPM.3', 'TOTAL GAL.3', 'GPM.4', 'TOTAL GAL.4', 'GPM.5', 'TOTAL GAL.5', 'GPM.6', 'TOTAL GAL.6', 'GPM.7', 'TOTAL GAL.7', 'GPM.8', 'TOTAL GAL.8', 'GPM.9', 'TOTAL GAL.9', 'GPM.10', 'TOTAL GAL.10', 'GPM.11', 'TOTAL GAL.11', 'GPM.12', 'TOTAL GAL.12', 'GPM.13', 'TOTAL GAL.13', 'GPM.14', 'TOTAL GAL.14', 'GPM.15', 'TOTAL GAL.15', 'GPM.16', 'TOTAL GAL.16', 'GPM.17', 'TOTAL GAL.17', 'GPM.18', 'TOTAL GAL.18', 'GPM.19', 'TOTAL GAL.19', 'GPM.20', 'TOTAL GAL.20', 'GPM.21', 'TOTAL GAL.21', 'GPM.22', 'TOTAL GAL.22', 'GPM.23', 'TOTAL GAL.23', 'comments', 'Unnamed: 51', 'Unnamed: 52', 'Unnamed: 53', 'Unnamed: 54', 'Unnamed: 55', 'Unnamed: 56', 'Unnamed: 57', 'Unnamed: 58', 'Unnamed: 59', 'Unnamed: 60', 'Unnamed: 61', 'Unnamed: 62', 'Unnamed: 63', 'Unnamed: 64', 'Unnamed: 65', 'Unnamed: 66', 'Unnamed: 67', 'Unnamed: 68', 'Unnamed: 69', 'Unnamed: 70', 'Unnamed: 71', 'Unnamed: 72', 'Unnamed: 73', 'Unnamed: 74', 'Unnamed: 75', 'Unnamed: 76']
# col = ['Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']# ['row_id', 'Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']
# col2 = [ 'Date', 'Time','GPM_25', 'TOTAL_GAL_25', 'GPM_26','TOTAL_GAL_26','GPM_27', 'TOTAL_GAL_27', 'GPM_28','TOTAL_GAL_28', 'GPM_29', 'TOTAL_GAL_29', 'GPM_30','TOTAL_GAL_30', 'GPM_31', 'TOTAL_GAL_31', 'GPM_32', 'TOTAL_GAL_32', 'GPM_33','TOTAL_GAL_33', 'GPM_34', 'TOTAL_GAL_34', 'GPM_35', 'TOTAL_GAL_35', 'GPM_36','TOTAL_GAL_36', 'GPM_37', 'TOTAL_GAL_37', 'GPM_38', 'TOTAL_GAL_38', 'GPM_39','TOTAL_GAL_39', 'GPM_40', 'TOTAL_GAL_40', 'GPM_41', 'TOTAL_GAL_41','GPM_42', 'TOTAL_GAL_42', 'GPM_43', 'TOTAL_GAL_43', 'GPM_44','TOTAL_GAL_44', 'GPM_45', 'TOTAL_GAL_45', 'GPM_101', 'TOTAL_GAL_101','GPM_102', 'TOTAL_GAL_102', 'GPM_103', 'TOTAL_GAL_103', 'GPM_104','TOTAL_GAL_104', 'GPM_105', 'TOTAL_GAL_105', 'GPM_106', 'TOTAL_GAL_106','GPM_107', 'TOTAL_GAL_107', 'comments', 'datetime']

# Get a list of columns from the corrected df and set its' columns to be the columns of the dirty data frame
new_columns = (list(df1.columns))
print(type(list(df1.columns)))
print(new_columns)

df2.columns = new_columns

# verify that they are the same 

print(df1["GPM.1"], df2["GPM.1"])

# once the df are normalized you can beign counting the number if new rows that need to be added to the data base. 

# Helper function for generating containers 

import streamlit as st 

for i in range(13):  # 13 rows
    cols = st.columns(4)  # 4 columns
    
    for j in range(4):
        with cols[j]:
            st.container().write(f"Row {i+1}, Col {j+1}")














