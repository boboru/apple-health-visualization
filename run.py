import streamlit as st

pg = st.navigation(
    [
        st.Page("home.py", title="Home", icon=":material/home:"),
        st.Page("sleep_analysis.py", title="Overall Sleep", icon=":material/bedtime:"),
        st.Page("one_night.py", title="One Night Sleep", icon=":material/sleep_score:")]
)
pg.run()
