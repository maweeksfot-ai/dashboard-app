import sys
import os
import pandas as pd
import streamlit as st
from datetime import datetime, time
import altair as alt
from utils.data_pipeline import load_all_data


st.set_page_config(layout="wide")

sys.path.append(os.path.join(os.getcwd(), "..", "data"))

live_urls = [ "https://1drv.ms/x/c/d6aca2526f83594b/IQAMcIopdLU9SINiVRsgBHwWAZsXQJ5-PHSv1BevGvZ8f0Q?download=1",
              "https://1drv.ms/x/c/d6aca2526f83594b/IQAlE6FfCDS_QL0HXfdxWdtCAae3Ilx-a_K9hA_PXGN3Ofs?download=1"
               ]

columns1 = ['Date', 'Time', 'GPM_1', 'TOTAL_GAL_1', 'GPM_2','TOTAL_GAL_2', 'GPM_3', 'TOTAL_GAL_3', 'GPM_4', 'TOTAL_GAL_4', 'GPM_5','TOTAL_GAL_5', 'GPM_6', 'TOTAL_GAL_6', 'GPM_7', 'TOTAL_GAL_7', 'GPM_8','TOTAL_GAL_8', 'GPM_9', 'TOTAL_GAL_9', 'GPM_10', 'TOTAL_GAL_10', 'GPM_11','TOTAL_GAL_11', 'GPM_12', 'TOTAL_GAL_12', 'GPM_13', 'TOTAL_GAL_13','GPM_14', 'TOTAL_GAL_14', 'GPM_15', 'TOTAL_GAL_15', 'GPM_16','TOTAL_GAL_16', 'GPM_17', 'TOTAL_GAL_17', 'GPM_18', 'TOTAL_GAL_18','GPM_19', 'TOTAL_GAL_19', 'GPM_20', 'TOTAL_GAL_20', 'GPM_21','TOTAL_GAL_21', 'GPM_22', 'TOTAL_GAL_22', 'GPM_23', 'TOTAL_GAL_23','GPM_24', 'TOTAL_GAL_24', 'comments', 'datetime']
columns2 = ['Date', 'Time','GPM_25', 'TOTAL_GAL_25', 'GPM_26','TOTAL_GAL_26','GPM_27', 'TOTAL_GAL_27', 'GPM_28','TOTAL_GAL_28', 'GPM_29', 'TOTAL_GAL_29', 'GPM_30','TOTAL_GAL_30', 'GPM_31', 'TOTAL_GAL_31', 'GPM_32', 'TOTAL_GAL_32', 'GPM_33','TOTAL_GAL_33', 'GPM_34', 'TOTAL_GAL_34', 'GPM_35', 'TOTAL_GAL_35', 'GPM_36','TOTAL_GAL_36', 'GPM_37', 'TOTAL_GAL_37', 'GPM_38', 'TOTAL_GAL_38', 'GPM_39','TOTAL_GAL_39', 'GPM_40', 'TOTAL_GAL_40', 'GPM_41', 'TOTAL_GAL_41','GPM_42', 'TOTAL_GAL_42', 'GPM_43', 'TOTAL_GAL_43', 'GPM_44','TOTAL_GAL_44', 'GPM_45', 'TOTAL_GAL_45', 'GPM_101', 'TOTAL_GAL_101','GPM_102', 'TOTAL_GAL_102', 'GPM_103', 'TOTAL_GAL_103', 'GPM_104','TOTAL_GAL_104', 'GPM_105', 'TOTAL_GAL_105', 'GPM_106', 'TOTAL_GAL_106','GPM_107', 'TOTAL_GAL_107', 'comments', 'datetime']

if st.button("Refresh Data"):
    load_all_data.clear()

st.session_state.df_tidy, st.session_state.df_combined = load_all_data(
    live_urls, columns1, columns2
)


df_tidy = st.session_state.df_tidy
df_combined = st.session_state.df_combined


def main():

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False

    # st.dataframe(df_tidy)
    st.header("Total Gallons By Pump")
    pump = st.selectbox("Select Pump", sorted(df_tidy['pump'].unique()))
    filtered = df_tidy[df_tidy['pump'] == pump]
    st.line_chart(filtered.set_index('datetime')['TOTAL_GAL'])


###################################################################

    df_tidy['datetime'] = pd.to_datetime(df_tidy['datetime'])
    # Set datetime as index
    df_tidy_indexed = df_tidy.set_index('datetime')
    # Group by pump and resample weekly
    weekly = (df_tidy_indexed.groupby('pump')['TOTAL_GAL'].resample('W')  # weekly frequency
        .agg(first='first', last='last')
        .reset_index()  # bring 'pump' back as column
)   
    

    weekly['weekly_volume'] = (weekly['last'] - weekly['first']).clip(lower=0)

    pump_options = sorted(df_tidy['pump'].unique())
    selected_pump = st.selectbox("Select Pump", pump_options, key="b")

    weekly_filtered = weekly[weekly['pump'] == (selected_pump)]

    bar_chart = alt.Chart(weekly_filtered).mark_bar(point=True).encode(
        x='datetime:T',
        y='weekly_volume:Q',
        color='pump:N',
        tooltip=['pump', 'datetime', 'weekly_volume']).interactive()
    st.altair_chart(bar_chart, width='stretch')

    pump_options1 = sorted(df_tidy['pump'].unique())
    selected_pumps1 = st.multiselect("Select Pumps", pump_options1, default=[pump_options1[0]])


    # Date slider
    min_date = weekly['datetime'].min().date()
    max_date = weekly['datetime'].max().date()
    start_date, end_date = st.slider(
        "Select date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    # Filter the data
    weekly_filtered1 = weekly[
        (weekly['pump'].isin(selected_pumps1)) &
        (weekly['datetime'].dt.date >= start_date) &
        (weekly['datetime'].dt.date <= end_date)
    ]

    # Plot
    line_chart = alt.Chart(weekly_filtered1).mark_line(point=True).encode(
        x='datetime:T',
        y='weekly_volume:Q',
        color='pump:N',
        tooltip=['pump', 'datetime', 'weekly_volume']
    ).interactive()

    st.altair_chart(line_chart, width='stretch')


    def plot_volume_last_2_weeks(df):
        # Ensure datetime is correct
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Filter last 2 weeks
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=14)
        df_recent = df[df['datetime'] >= cutoff].copy()

        # Sort for proper diff calculation
        df_recent = df_recent.sort_values(['pump', 'datetime'])

        # Calculate volume between measurements
        df_recent['volume'] = df_recent.groupby('pump')['TOTAL_GAL'].diff()

        # Optional: remove negative or NaN values (resets, first row per pump)
        df_recent = df_recent[df_recent['volume'] > 0]

        # Create chart
        chart = alt.Chart(df_recent).mark_line().encode(
            x='datetime:T',
            y='volume:Q',
            color='pump:N',
            tooltip=['pump', 'datetime', 'volume']
        ).properties(
            title='Volume Between Measurements (Last 2 Weeks)'
        )

        return chart

    chart = plot_volume_last_2_weeks(df_tidy)
    st.altair_chart(chart, use_container_width=True)
    # # =========================
    # # 🔹 STREAMLIT UI
    # # =========================
    # df_combined, df_daily, runtime, totals = run_analysis(df_combined)

    # st.title("Pump Dashboard")

    # # ---- Total System Flow ----
    # st.subheader("Total System GPM Over Time")
    # st.line_chart(df_combined.set_index('datetime')['total_GPM'])

    # # ---- Daily Total ----
    # st.subheader("Daily Total GPM")
    # st.line_chart(df_daily['total_GPM'])

    # # ---- Pump Selection ----
    # gpm_cols = [col for col in df_combined.columns if 'GPM_' in col]
    # pump = st.selectbox("Select Pump", gpm_cols)

    # st.subheader(f"{pump} Over Time")
    # st.line_chart(df_combined.set_index('datetime')[pump])

    # # ---- Runtime ----
    # st.subheader("Pump Runtime %")
    # st.bar_chart(runtime)

    # # ---- Total Usage ----
    # st.subheader("Pump Total Usage")
    # st.bar_chart(totals)

    # # ---- Spikes ----
    # st.subheader("Spike Detection")
    # spikes = get_spikes(df_combined, pump)
    # st.write(spikes)


main()
