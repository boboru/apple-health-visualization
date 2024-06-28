import argparse
import os
from pathlib import Path

import streamlit as st

parser = argparse.ArgumentParser(description="Visualizes your Apple Health data")

parser.add_argument(
    "-f",
    "--file",
    default="export.feather",
    type=str,
    help="path of exported feather file",
)

try:
    args = parser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)

xml_path = Path(args.file)
if not xml_path.exists():
    raise FileNotFoundError("XML file not found")
else:  # save to session
    st.session_state.data_path = xml_path

st.set_page_config(
    page_title="Apple Health Visualization",
    page_icon=":apple:",
)

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)
