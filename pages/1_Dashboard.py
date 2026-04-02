import streamlit as st
import json
from streamlit_lottie import st_lottie
import sys
import os
import pandas as pd
import numpy as np 
import math
from PIL import Image
import requests
from io import BytesIO

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
from data.deep_well import DeepWell



test_data_url_1 = "https://1drv.ms/x/c/f6261b79731e452c/IQBpBPUwwVtQTYrz4LgAWE6ZAfTxxxhud5AzyDm4tVY5P-0?download=1"
test_data_url_2 = "https://1drv.ms/x/c/f6261b79731e452c/IQDTm4wgClDgRKutu40S_fAUASzQrkvm2Z--Qe2whPBX1xI?download=1"

st.set_page_config(layout="wide")

# Load logo
logo = Image.open("assets/maweeks.png")  # make sure path is correct

# Create three columns: logo | title | empty (for spacing)
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.image(logo, width=120)  # Logo on left

with col2:
    st.markdown(
        "<h1 style='text-align: center;'>Deep Well Dashboard</h1>",
        unsafe_allow_html=True
    )

with col3:
    st.write("")  # Empty column for spacing

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


def get_data(url, ttl=1800):
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
    # df = pd.read_csv(fd, sep='\t', header=None, skip_blank_lines=True)
    df = df.replace(',', '', regex=True)
    df = df.dropna(how="all")
    return df

@st.cache_data
def make_request(url1, url2):
    df1 = get_data(url1)
    df2 = get_data(url2)
    return df1, df2

@st.cache_data
def open_csv(fd):
    df = pd.read_csv(fd, sep='\t', header=None, skip_blank_lines=True)
    df = df.replace(',', '', regex=True)
    df = df.dropna(how="all")
    return df

def parse_value(val, is_percent=False):
    """
    Convert cell safely:
    - '#NA', blank → None
    - '33%' → 33.0
    - fractions like 0.05 → 5 if is_percent=True
    - numbers → float
    """
    if pd.isna(val) or str(val).strip() in ("", "#NA"):
        return None
    
    val_str = str(val).replace(",", "").replace("%", "")
    
    try:
        num = float(val_str)
        if is_percent and 0 < num < 1:
            # Convert fraction to percent
            return num * 100
        return num
    except ValueError:
        return None
    
def parse_wells_from_row(row, start_id=1, skip_cols=3):
    """
    Parse a DataFrame row into wells.
    
    row: pd.Series, one row of data
    start_id: starting well number
    skip_cols: number of columns at the start to skip (timestamps, NaN)
    
    Returns: dict of well_id -> DeepWell objects
    """
    wells = {}
    
    # Start parsing after skip_cols
    data_cols = row.iloc[skip_cols:].reset_index(drop=True)
    
    for i in range(0, len(data_cols), 2):
        well_id = start_id + i // 2
        
        gpm = parse_value(data_cols[i])
        total = parse_value(data_cols[i + 1]) if i + 1 < len(data_cols) else None
        wells[well_id] = DeepWell(
            well_id=well_id,
            gpm=gpm,
            total=total
        )
    
    return wells

def load_lottie_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)
    
def get_animation_speed(gpm):
    if gpm is None:
        return 0  # no animation
    if gpm == 0:
        return 0.2
    return min(3, 0.5 + math.log1p(gpm))


def get_status(gpm):
    if gpm is None:
        return "NO DATA", "gray"
    elif gpm == 0:
        return "OFF", "red"
    elif gpm < 10:
        return "LOW", "orange"
    else:
        return "NORMAL", "blue"
    

def format_values(gpm, total, gpm_is_percent=False):
    gpm_display = "N/A" if gpm is None else f"{gpm} gal/min"
    if gpm is None:
        gpm_display = "N/A"
    else:
        if gpm_is_percent:
            val = gpm * 100
            gpm_display = f"{val:.1f}%"  # Show percent
        else:
            gpm_display = f"{gpm:,} gal/min"
    if gpm is None:
        gpm = "N/A"

    total_display = f"{total:} gal"
    return gpm_display, total_display

@st.cache_data
def get_animation():
    return load_lottie_file("assets/water.json")


# df1 = open_csv("data\\list_a.csv")
# df2 = open_csv("data\\list_b.csv")

# df1 = get_data(ONEDRIVE_URL1)
# df2 = get_data(ONEDRIVE_URL2)

df1, df2 = make_request(test_data_url_1, test_data_url_2)
# print(df1)


latest_row1 = df1.iloc[-1, :51]
latest_row2 = df2.iloc[-1, :59]

last_reading = latest_row1.iloc[2]
# Parse wells
wells1 = parse_wells_from_row(latest_row1)
wells2 = parse_wells_from_row(latest_row2, start_id=len(wells1) + 1)

# print(wells1)

# Get sorted well IDs from wells2
wells2_keys = sorted(wells2.keys())

# Last 7 wells
last_7_keys = wells2_keys[-7:]

# New mapping starting at 101
remapped_wells = {}



for idx, old_key in enumerate(last_7_keys):
    new_id = 101 + idx
    well = wells2[old_key]
    
    # Update the object's ID
    well.well_id = new_id
    
    remapped_wells[new_id] = well

# Remove old keys
for key in last_7_keys:
    del wells2[key]

# Add remapped wells back in
wells2.update(remapped_wells)

# Combine into a single dict
wells = {**wells1, **wells2}

# df = pd.concat([df1, df2], ignore_index=True)

if "wells" not in st.session_state:
    st.session_state.wells = wells
else:
    st.session_state.wells.update(wells)

# Calculate totals
total_gpm = sum(w.gpm for w in st.session_state.wells.values() if w.gpm is not None)
total_gallons = sum(w.total for w in st.session_state.wells.values() if w.total is not None)

if st.button("🔄 Refresh Data"):
    make_request.clear()  # clears cache for this function

    
st.write("")
# Display metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Site Flow", f"{total_gpm:.1f} gal/min")

with col2:
    st.metric("Total Pumped", f"{total_gallons:,.0f} gal")
with col3:
    st.metric("Last Reading", f"{last_reading}")

COLS = 4  # Number of columns per row

# Assume st.session_state.wells is already populated with DeepWell objects
wells_list = list(st.session_state.wells.values())


# Load Lottie animation once
@st.cache_data
def load_lottie():
    import json
    with open("assets/water.json", "r") as f:
        return json.load(f)

lottie_water = load_lottie()

# Loop over wells in grid
for i in range(0, len(wells_list), COLS):
    cols = st.columns(COLS)
    
    for j, col in enumerate(cols):
        if i + j >= len(wells_list):
            continue
        
        well = wells_list[i + j]
        # print(well)
        gpm = well.gpm
        # Derived values
        speed = get_animation_speed(gpm)   # Your function
        status, color = get_status(gpm)    # Your function
        # total = well.total
        # print(total, i, j)
        # if well.total is not None:
        #     total = well.total
        # else:
        #     count = 1
        #     while total is None:
        #         total = wells_list[(i + j) - count].total
        #         count += 1
        #         print(well.total)
        #     print("total: ", (total), i, j,  gpm, total)

        with col:
            with st.container(border=True):
                st.subheader(f"DW {well.well_id}")

                # Status bar
                st.markdown(
                    f"<div style='height:6px;background:{color};border-radius:4px;'></div>",
                    unsafe_allow_html=True
                )

                # Status label
                if status == "NO DATA":
                    st.info("⚪ No Data")
                elif status == "OFF":
                    st.error("🔴 OFF")
                elif status == "LOW":
                    st.warning("🟡 LOW FLOW")
                else:
                    st.success("🔵 NORMAL")

                # Lottie animation
                if gpm is not None:
                    st_lottie(
                        lottie_water,
                        height=80,
                        speed=speed,
                        key=f"lottie_{well.well_id}"
                    )

                if gpm is None:
                    pass
                else:
                    gpm_is_percent = True if well.gpm < 1 else False  # crude check: <1 → percentage


                gpm_display, total_display = format_values(gpm, well.total, gpm_is_percent)

                if well.total is None:
                    total_display = "Unreadable"
                else:
                    total_display = well.total
                
                st.metric("GPM", gpm_display)
                st.metric("Total", total_display)

                st.markdown("---")  # Divider before issues




