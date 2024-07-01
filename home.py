import argparse
import os
from pathlib import Path
import streamlit as st
from simulate import simulate

def update_dir(key):
    choice = st.session_state[key]
    if os.path.isdir(os.path.join(st.session_state[key+'curr_dir'], choice)):
        st.session_state[key+'curr_dir'] = os.path.normpath(os.path.join(st.session_state[key+'curr_dir'], choice))
        files = sorted(os.listdir(st.session_state[key+'curr_dir']))
        files.insert(0, '..')
        files.insert(0, '.')
        st.session_state[key+'files'] = files

def st_file_selector(st_placeholder, path='.', label='Select a file/folder', key='selected'):
    if key+'curr_dir' not in st.session_state:
        base_path = '.' if path is None or path is '' else path
        base_path = base_path if os.path.isdir(base_path) else os.path.dirname(base_path)
        base_path = '.' if base_path is None or base_path is '' else base_path

        files = sorted(os.listdir(base_path))
        files.insert(0, '..')
        files.insert(0, '.')
        st.session_state[key+'files'] = files
        st.session_state[key+'curr_dir'] = base_path
    else:
        base_path = st.session_state[key+'curr_dir']

    selected_file = st_placeholder.selectbox(label=label, 
                                        options=st.session_state[key+'files'], 
                                        key=key, 
                                        on_change = lambda: update_dir(key))
    selected_path = os.path.normpath(os.path.join(base_path, selected_file))
    #st_placeholder.write(os.path.abspath(selected_path))

    return selected_path


parser = argparse.ArgumentParser(description="Visualizes your Apple Health data")

parser.add_argument(
    "-f",
    "--file",
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

if args.file:
    path = Path(args.file)
    if not path.exists():
        raise FileNotFoundError("File not found")
    else:  # save to session
        st.session_state.data_path = path
else:
    st.session_state.data_path = None

st.session_state.using_fake = False
st.session_state.df = None

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
        
"""
)

with st.container(height=420):
    st.write("## Import Data")
    tab1, tab2 = st.tabs(["Select a File", "Generate Fake Data"])
    with tab1:
        st.markdown("""
        To use your own data, please follow the instrucions on [GitHub](https://github.com/boboru/apple-health-visualization) to export data from Apple Health.
        """)

        file_path = st_file_selector(st, label='Select a  `.feather`  file')
        path = Path(file_path)
        if st.button('Import', type="primary"):
            if path.exists():
                filename, file_extension = os.path.splitext(file_path)
                if (file_extension == ".feather") or (file_extension == ".csv"):
                    st.success("Success!", icon="✨")
                    st.session_state.data_path = file_path
                    st.session_state.using_fake = False
                else:
                    st.error("Please select a `.feather`  file.", icon="❌")
            else:
                st.error("File not found.", icon="❌")

            st.session_state.df = None 
            st.cache_data.clear()

    with tab2:
        if st.button('Generate', type="primary"):
            df = simulate()
            st.success("Success!", icon="✨")
            st.write(df.head(10))
            st.session_state.df = df
            st.session_state.using_fake = True
            st.cache_data.clear()

st.write("**👈 Select an analysis from the sidebar**")


st.divider()
st.markdown(
    """
    ### Contact
    - email: boru0713@gmail.com
    - [GitHub](https://github.com/boboru/apple-health-visualization)
    - [Blog](https://boboru.net/) 
    """
)