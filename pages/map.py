import streamlit as st
import pandas as pd

st.title("Site Map")

st.write("Map placeholder — add well coordinates later.")

# Example dummy map data
data = pd.DataFrame({
    "lat": [41.626759],
    "lon": [-111.876478]
})
#  41.626759, -111.876478


st.map(data)