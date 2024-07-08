## Interactive Stock Price Analysis with Dynamic Visualization (Dash)

This Dash app allows you to interactively explore and visualize historical stock price data. It provides functionalities to:

* **Overlay recent months on top of long-term data:**  
  - View both a 5-year historical trend and the most recent 3 months in detail.
  - Adjust the timeframe of the 3-month data by dragging the "3-Month Move Slider".
* **Customize the visualization:**
  - Scale the Y-axis (price) and X-axis (date range) of the 3-month data independently using sliders.
  - Apply a vertical offset to the 3-month data for better alignment.
  - Enable logarithmic scaling on the price axis for enhanced visualization of large fluctuations.
* **Calculate the best fit:**
  - Click the "Calculate Best Fit" button to automatically optimize the visualization parameters (month move, scaling factors, and offset) to minimize the difference between the 5-year and 3-month data. 

**Data Requirements:**

* A CSV file containing historical daily stock data (named "Daily2020.csv" in this example). 
  - Ensure it has a "Date" column in a datetime format and a "Close" (or "Open") column for price data.

**Running the App:**

1. Save the script as a Python file (e.g., stock_explorer.py).
2. Install required libraries: `pip install pandas dash plotly numpy scipy`
3. Place your CSV data file in the same directory as the script.(download fresh data from Nasdaq)
4. Verify the name of the file in the python file is correct. e.g. `file_path = "./<fileName>.csv`
4. Run the script: `python align_stock_data.py`
5. Open http://127.0.0.1:8050/ in your web browser to interact with the app.

**Disclaimer:** This is for educational and informational purposes only. It should not be considered financial advice.
