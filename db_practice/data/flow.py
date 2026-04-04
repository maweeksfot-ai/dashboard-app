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














