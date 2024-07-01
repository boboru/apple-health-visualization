# Apple Health Visualization (streamlit + altair)
This application visualizes your Apple Health data with ease. Unlike the built-in iOS app, it allows you to effortlessly select and explore your desired time range.

To protect your privacy, your Apple Health data is utilized locally. Otherwise, we perform simulated data generation. (ignore step 2.)

Start using demo:

![img](image/img1.png)


## Quick Start

1. Install package (poetry)
    ```
    poetry install
    ```
2. (Optional) Export your data from Apple Health app
    1. Open your Apple Health / Click user profile / Export 
    ![export](image/export.png)
    2. Run the script to export a `.feather` file
    ```
    # poetry run python -m apple_health_exporter [exported zip file from Health] [.feather file name]

    poetry run python -m apple_health_exporter export.zip export.feather
    ```
3. Run Streamlit
   ```
   poetry run streamlit run run.py
   ```

  
Import data or use fake data and start!
![import](image/import.png)


## Contact
- [GitHub](https://github.com/boboru/apple-health-visualization)
- [Blog](https://boboru.net/) 