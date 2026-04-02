import pandas as pd
import sqlite3
from io import BytesIO
import requests
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
# ---------- 1. List of OneDrive URLs ----------
urls = [
    "https://1drv.ms/x/c/f6261b79731e452c/IQBpBPUwwVtQTYrz4LgAWE6ZAfTxxxhud5AzyDm4tVY5P-0?download=1",  # First spreadsheet
    "https://1drv.ms/x/c/f6261b79731e452c/IQDTm4wgClDgRKutu40S_fAUASzQrkvm2Z--Qe2whPBX1xI?download=1"   # Second spreadsheet
]

# ---------- 2. Download and process each sheet ----------
long_rows = []

for url in urls:
    resp = requests.get(url)
    excel_file = BytesIO(resp.content)
    
    # Load Excel with multi-header
    df = pd.read_excel(excel_file, header=[0,1], index_col=[0,1])
    
    # Flatten multi-level columns
    df.columns = ['_'.join([str(c) for c in col if c]).strip('_') for col in df.columns.values]
    
    # Reset index to access Reading Date / Time
    df = df.reset_index()
    
    # Dynamically find date/time columns
    date_col = [c for c in df.columns if 'Reading Date' in c][0]
    time_col = [c for c in df.columns if 'Reading Time' in c][0]
    
    # Identify well columns (all other columns except date/time)
    well_cols = [c for c in df.columns if c not in [date_col, time_col]]
    
    for i, well in enumerate(well_cols):
        temp = df[[date_col, time_col, well]].copy()
        temp = temp.rename(columns={well: 'total_gal'})
        
        # Try to find corresponding GPM column
        gpm_col = well.replace('Total Gal', 'GPM')
        temp['gpm'] = df[gpm_col] if gpm_col in df.columns else None
        
        # Assign custom well IDs
        temp['well_id'] = str(i + 1) if i < 45 else str(101 + (i - 45))
        
        # Create datetime column
        temp['reading_datetime'] = pd.to_datetime(
            temp[date_col].astype(str) + ' ' + temp[time_col].astype(str)
        )
        
        # Keep only required columns
        long_rows.append(temp[['well_id', 'reading_datetime', 'gpm', 'total_gal']])

# ---------- 3. Combine all wells into one DataFrame ----------
long_df = pd.concat(long_rows, ignore_index=True)
long_df.sort_values(['well_id', 'reading_datetime'], inplace=True)

# ---------- 4. Prepare SQLite database ----------
db_path = "data/well_readings.db"
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS well_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id TEXT,
    reading_datetime TEXT,
    gpm REAL,
    total_gal REAL,
    latest_total REAL
)
""")
conn.commit()

# ---------- 5. Insert only new rows ----------
for well in long_df['well_id'].unique():
    well_df = long_df[long_df['well_id'] == well].sort_values('reading_datetime')
    
    # Last recorded datetime in DB
    cursor.execute("SELECT MAX(reading_datetime) FROM well_readings WHERE well_id = ?", (well,))
    res = cursor.fetchone()
    last_db_time = pd.to_datetime(res[0]) if res[0] else None
    
    # Filter only new rows
    new_rows = well_df[well_df['reading_datetime'] > last_db_time] if last_db_time else well_df
    
    # Get last latest_total in DB
    cursor.execute(
        "SELECT latest_total FROM well_readings WHERE well_id = ? ORDER BY reading_datetime DESC LIMIT 1", 
        (well,)
    )
    res = cursor.fetchone()
    last_total = res[0] if res and res[0] is not None else None
    
    # Insert new rows
    for _, row in new_rows.iterrows():
        latest_total = row['total_gal'] if pd.notna(row['total_gal']) else last_total
        cursor.execute("""
        INSERT INTO well_readings (well_id, reading_datetime, gpm, total_gal, latest_total)
        VALUES (?, ?, ?, ?, ?)
        """, (row['well_id'], row['reading_datetime'], row['gpm'], row['total_gal'], latest_total))
        last_total = latest_total

conn.commit()
conn.close()

print("Database updated successfully from multiple OneDrive URLs!")