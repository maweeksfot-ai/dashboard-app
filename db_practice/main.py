import sys
import os
import requests
import pandas as pd
import sqlite3
from io import BytesIO


urls = [
    "https://1drv.ms/x/c/f6261b79731e452c/IQBpBPUwwVtQTYrz4LgAWE6ZAfTxxxhud5AzyDm4tVY5P-0?download=1",  # First spreadsheet
    # "https://1drv.ms/x/c/f6261b79731e452c/IQDTm4wgClDgRKutu40S_fAUASzQrkvm2Z--Qe2whPBX1xI?download=1"   # Second spreadsheet
]

def get_data(url):
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
    # df = pd.read_csv(fd, sep='\t', header=None, skip_blank_lines=True)
    df = df.replace(',', '', regex=True)
    df = df.dropna(how="all")
    return df

print("PROGRAM RUNNNIN ...", "\n\n\n")

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))

for url in urls:
    # resp = requests.get(url)
    # excel_file = BytesIO(resp.content)
    df = get_data(url)

print(df[-1: 2])
print(type(df))
print("\n\n\n PROGRAM DONE RUNNING ... ")
