from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


@st.cache_data
def get_df():
    return pd.read_feather(st.session_state.data_path)

def timedelta_to_hourminute(dt):
    return f'{dt // 3600:.0f}h {(dt//60) % 60:.0f}m'


st.set_page_config(
    page_title="Sleep Analysis",
    page_icon=":apple:",
)

st.markdown("# Sleep Analysis")
st.sidebar.header("Setting")
st.write("""Choose start date and end date to analyze your daily in bed time.""")

# get data and limited its range
df = get_df()
df = df.loc[df["value"] == "HKCategoryValueSleepAnalysisInBed"]
date_col = ["startDate", "endDate"]
df[date_col] = (
    df[date_col]
    .apply(lambda x: x.dt.strftime("%Y-%m-%dT%H:%M:%S"))
    .apply(pd.to_datetime)
)
df["duration"] = df["endDate"] - df["startDate"]
df = df.loc[df["duration"] >= timedelta(minutes=5)]  # remove durations <= 5 minutes
# D0 sleep: D0 18:00 - D1 18:00
df["idx"] = df["startDate"].apply(
    lambda x: x.date() if x.hour >= 18 else x.date() - timedelta(days=1)
)

start_date = st.date_input(
    "Start date",
    value=df["idx"].min(),
    min_value=df["idx"].min(),
    max_value=df["idx"].max(),
)
end_date = st.date_input(
    "End date",
    value=df["idx"].max(),
    min_value=df["idx"].min(),
    max_value=df["idx"].max(),
)
df = df.loc[df["idx"].between(start_date, end_date)]

area_df = df.groupby("idx").duration.sum().reset_index()
area_df["duration"] = area_df["duration"].dt.total_seconds()


c = (
    (
        alt.Chart(area_df)
        .mark_area()
        .encode(
            x=alt.X("idx").title("date"),
            y=alt.Y("duration").axis(
                labelExpr='floor(datum.value/3600)+"h "+floor((datum.value%3600)/60)+"m"'
            ),
        )
    )
    .properties(title=alt.Title("In Bed Time", fontSize=24))
    .interactive()
)

st.markdown("###")

st.altair_chart(c, use_container_width=True)

# Add metrics
col1, col2, col3 = st.columns(3)
q1 = np.quantile(area_df["duration"], 0.25)
q2 = np.quantile(area_df["duration"], 0.5)
q3 = np.quantile(area_df["duration"], 0.75)

col1.metric(label="Median", value=timedelta_to_hourminute(q2), help='50% percentile') 
col2.metric(label="Q1", value=timedelta_to_hourminute(q1), help='25% percentile')
col3.metric(label="Q3", value=timedelta_to_hourminute(q3), help='75% percentile')
