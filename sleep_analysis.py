from datetime import timedelta, time, datetime
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import os

@st.cache_data
def get_df():
    if st.session_state.using_fake:
        df = st.session_state.df
    else:
        path = st.session_state.data_path
        filename, file_extension = os.path.splitext(path)
        if file_extension == ".feather":
            df = pd.read_feather(path)
        elif file_extension == ".csv":
            df = pd.read_csv(
                path, parse_dates=["startDate", "endDate"], date_format="%Y-%m-%d %H:%M:%S"
            )
        else:
            raise IOError(
                "Unsupported file types. Currently supports .csv or .feather file."
            )

    df.drop_duplicates(inplace=True)

    df = df.loc[df["value"] == "HKCategoryValueSleepAnalysisInBed"]
    date_col = ["startDate", "endDate"]

    df[date_col] = df[date_col].apply(
        lambda x: pd.to_datetime(x.dt.strftime(date_format='%Y-%m-%d %H:%M:%S'), 
        format='%Y-%m-%d %H:%M:%S'),
        axis=1,
    )

    df["duration"] = df["endDate"] - df["startDate"]
    df = df.loc[df["duration"] >= timedelta(minutes=5)]  # remove durations <= 5 minutes
    # D0 sleep: D0 18:00 - D1 18:00
    df["idx"] = df["startDate"].apply(
        lambda x: x.date() if x.hour >= 18 else x.date() - timedelta(days=1)
    )

    return df


def timedelta_to_hourminute(dt):
    return f"{dt // 3600:.0f}h {(dt//60) % 60:.0f}m"


st.set_page_config(
    page_title="Overall Sleep",
    page_icon=":apple:",
)

st.markdown("# Overall Sleep")
st.write("""Choose start date and end date to analyze your daily sleep time.""")

if "data_path" not in st.session_state:
    st.session_state.data_path = None
if "df" not in st.session_state:
    st.session_state.df = None
if "using_fake" not in st.session_state:
    st.session_state.using_fake = False

if st.session_state.data_path is None and st.session_state.df is None:
    st.warning("Please import data on Home page first.", icon="⚠️")
    if st.button("Home", type="primary"):
        st.switch_page("home.py")
else:
    # get data and limited its range
    df = get_df()

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

    area_base = alt.Chart(area_df)

    area_line = (
        area_base.mark_area()
        .encode(
            x=alt.X("idx").title("Date"),
            y=alt.Y("duration")
            .axis(labelExpr='floor(datum.value/3600)+"h "+floor((datum.value%3600)/60)+"m"')
            .title("Duration"),
        )
        .interactive()
    )

    st.markdown("###")
    st.subheader("In Bed Time")
    st.altair_chart(area_line, use_container_width=True)

    # Add metrics
    col1, col2, col3 = st.columns(3)
    q1 = np.quantile(area_df["duration"], 0.25)
    q2 = np.quantile(area_df["duration"], 0.5)
    q3 = np.quantile(area_df["duration"], 0.75)

    col1.metric(label="Median", value=timedelta_to_hourminute(q2), help="50% percentile")
    col2.metric(label="Q1", value=timedelta_to_hourminute(q1), help="25% percentile")
    col3.metric(label="Q3", value=timedelta_to_hourminute(q3), help="75% percentile")

    st.markdown("###")
    st.subheader("Bed Time and Wake Up Time")

    line_df = (
        df.groupby("idx").agg(
            bed_time=("startDate", "min"),
            wakeup_time=("endDate", "max"),
        )
    ).reset_index()

    line_df["idx"] = line_df["idx"].apply(lambda x: datetime.combine(x, time(hour=18)))
    line_df["bed_time"] -= line_df["idx"]
    line_df["wakeup_time"] -= line_df["idx"]
    # add date to simplify formatting
    line_df["bed_time"] = datetime(2024, 1, 1, 18, 0, 0) + line_df["bed_time"]
    line_df["wakeup_time"] = datetime(2024, 1, 1, 18, 0, 0) + line_df["wakeup_time"]
    line_df.rename(
        columns={"bed_time": "Bed Time", "wakeup_time": "Wake Up Time"}, inplace=True
    )


    hist_base = (
        alt.Chart(line_df)
        .transform_fold(["Bed Time", "Wake Up Time"], as_=["Type", "Time"])
        .transform_bin(field="Time", as_="Time", bin=alt.Bin(maxbins=100))
        .encode(
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(
                    domain=["Bed Time", "Wake Up Time"], range=["#ddccbb", "red"]
                ),
            ),
        )
    )

    hist_line = hist_base.mark_bar(opacity=0.4, binSpacing=0).encode(
        alt.X("Time:T").axis(format="%H:%M"),
        alt.Y("count()", stack=None),
    )

    hist_rule = hist_base.mark_rule(size=2).encode(
        alt.X("median(Time):T").axis(format="%H:%M"),
        tooltip=[
            alt.Tooltip("median(Time):T", format="%H:%M"),
        ],
    )

    st.altair_chart((hist_line + hist_rule).interactive(), use_container_width=True)

    # Add metrics
    col1, col2 = st.columns(2)
    bed_q2 = line_df["Bed Time"].median()
    wake_q2 = line_df["Wake Up Time"].median()

    col1.metric(
        label="Median of Bed Time", value=bed_q2.strftime("%H:%M"), help="50% percentile"
    )
    col2.metric(
        label="Median of Wake Up Time",
        value=wake_q2.strftime("%H:%M"),
        help="50% percentile",
    )
