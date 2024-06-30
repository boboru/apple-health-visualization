import argparse
import os
from pathlib import Path

import streamlit as st

parser = argparse.ArgumentParser(description="Visualizes your Apple Health data")

parser.add_argument(
    "-f",
    "--file",
    default="data/test.feather",
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

path = Path(args.file)
if not path.exists():
    raise FileNotFoundError("File not found")
else:  # save to session
    st.session_state.data_path = path

st.set_page_config(
    page_title="Apple Health Visualization",
    page_icon=":apple:",
)

st.write("# Apple Health Visualization")

st.markdown(
    """
    This application visualizes your Apple Health data with ease.
    Unlike the built-in iOS app, it allows you to effortlessly select and explore
    your desired time range.

    We temporarily provide overall and one-night sleep analysis.  
    **👈 Select an analysis from the sidebar**

    ## 
"""
)

st.divider()
st.markdown(
    """
    ### Contact
    - email: boru0713@gmail.com
    - [GitHub](https://github.com/boboru/apple-health-visualization)
    - [Blog](https://boboru.net/) 
    """
)