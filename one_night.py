import altair as alt
import pandas as pd
import streamlit as st
from datetime import timedelta
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

    df = df.loc[
        (df["type"] == "HKCategoryTypeIdentifierSleepAnalysis")
        | (df["type"] == "HKQuantityTypeIdentifierHeartRate")
    ]

    date_col = ["startDate", "endDate"]
    # apple health export useless time timezone offset (+/- hours:minutes) in export.xml
    df[date_col] = df[date_col].apply(
        lambda x: pd.to_datetime(
            x.dt.strftime(date_format="%Y-%m-%d %H:%M:%S"), format="%Y-%m-%d %H:%M:%S"
        ),
        axis=1,
    )

    # add time index
    # D0 sleep: D0 18:00 - D1 18:00
    df["idx"] = df["startDate"].apply(
        lambda x: x.date() if x.hour >= 18 else x.date() - timedelta(days=1)
    )

    return df


st.set_page_config(
    page_title="One Night Sleep",
    page_icon=":apple:",
)

st.markdown("# One Night Sleep")
st.write("""Choose one date to investigate your sleep.""")

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
    df = get_df()
    date_ = st.date_input(
        "Date",
        value=df["idx"].max(),
        min_value=df["idx"].min(),
        max_value=df["idx"].max(),
    )

    df = df[df["idx"] == date_]

    # sleep stages
    stage_df = df[df["type"] == "HKCategoryTypeIdentifierSleepAnalysis"]
    type_map = {
        "HKCategoryValueSleepAnalysisInBed": "In Bed",
        "HKCategoryValueSleepAnalysisAsleepCore": "Core",
        "HKCategoryValueSleepAnalysisAsleepREM": "REM",
        "HKCategoryValueSleepAnalysisAsleepDeep": "Deep",
        "HKCategoryValueSleepAnalysisAwake": "Awake",
    }

    stage_df = stage_df[["value", "startDate", "endDate"]]
    stage_df.rename(
        columns={"value": "type", "startDate": "start", "endDate": "end"}, inplace=True
    )
    stage_df["type"] = stage_df["type"].map(type_map)

    st.markdown("### ")
    st.subheader("Sleep Stages")
    st.altair_chart(
        alt.Chart(stage_df)
        .mark_bar()
        .encode(
            alt.X("start:T").title("Time"),
            alt.X2("end"),
            alt.Y("type").title("Type").sort(["In Bed", "Awake", "REM", "Core", "Deep"]),
            color=alt.Color(
                "type",
                scale=alt.Scale(
                    domain=["In Bed", "Awake", "REM", "Core", "Deep"],
                    range=["gray", "coral", "#77B0AA", "#135D66", "#003C43"],
                ),
                legend=alt.Legend(title="Type"),
            ),
            tooltip=[
                "type",
                alt.Tooltip("start:T", format="%H:%M"),
                alt.Tooltip("end:T", format="%H:%M"),
            ],
        )
        .interactive(),
        use_container_width=True,
    )

    st.caption("Different sleep stages are recorded by your Apple Watch :watch:.")


    # Combine heart rate
    st.markdown("### ")
    st.subheader("Heart Rate")

    heart_df = df.loc[df["type"] == "HKQuantityTypeIdentifierHeartRate"]
    heart_df.loc[:, "value"] = heart_df["value"].astype("int64")

    inbed_df = stage_df[stage_df["type"] == "In Bed"]
    stage_df = stage_df[stage_df["type"] != "In Bed"]
    y_min = heart_df["value"].min() - 5 if len(heart_df["value"]) != 0 else 70
    y_max = heart_df["value"].max() + 5 if len(heart_df["value"]) != 0 else 90

    inbed = (
        alt.Chart(inbed_df)
        .mark_bar(color="gray")
        .encode(
            alt.X("start:T").axis(orient="top").title(""),
            alt.X2("end"),
            alt.Y("type").title(""),
            tooltip=[
                "type",
                alt.Tooltip("start:T", format="%H:%M"),
                alt.Tooltip("end:T", format="%H:%M"),
            ],
        )
    )

    point = (
        alt.Chart(heart_df)
        .mark_point(color="#ddccbb", filled=True, opacity=1.0, size=50)
        .encode(
            x="endDate:T",
            y=alt.Y("value:Q", scale=alt.Scale(domainMin=y_min, domainMax=y_max)).title(
                "Heart Rate (BPM)"
            ),
        )
    )

    rect = (
        alt.Chart(stage_df)
        .mark_rect()
        .encode(
            alt.X("start:T").title("Time"),
            alt.X2("end:T"),
            color=alt.Color(
                "type",
                scale=alt.Scale(
                    domain=["Awake", "REM", "Core", "Deep"],
                    range=["coral", "#77B0AA", "#135D66", "#003C43"],
                ),
                legend=alt.Legend(title="Type"),
            ),
            tooltip=[
                "type",
                alt.Tooltip("start:T", format="%H:%M"),
                alt.Tooltip("end:T", format="%H:%M"),
            ],
            opacity=alt.value(0.5),
        )
    )

    st.altair_chart(
        alt.vconcat(inbed, (rect + point).resolve_scale(color="independent")).interactive(),
        use_container_width=True,
    )

    st.caption("Heart rate is also recorded by your Apple Watch :watch:.")
