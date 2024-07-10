# Interactive Stock Price Analysis with Dynamic Visualization (Dash)

This Dash app allows you to interactively explore and visualize historical stock price data. It provides functionalities to:

- **Overlay recent months on top of long-term data:**  
  - View both a 5-year historical trend and the most recent 3 months in detail(by default).
  - Adjust the timeframe of the 3-month data by dragging the "X-Axis Offset Slider".
  - set a custom date range for the overlay data by enabling "Use Custom Overlay Range".
  - set a custom date range for the static historic chart by modifying the "Custom Static Range".
- **Customize the visualization:**
  - Scale the Y-axis (price) and X-axis (date range) of the 3-month data independently using sliders.
  - Apply a vertical offset to the 3-month data for better alignment.
  - Enable logarithmic scaling on the price axis for enhanced visualization of large fluctuations.
- **Calculate the best fit:**
  - Click the "Calculate Best Fit" button to automatically optimize the visualization parameters (month move, scaling factors, and offset) to minimize the difference between the 5-year and 3-month data(This doesn't work well).

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

To run the app, run the following from the root directory:

```bash
python app.py
```

## Updating/Adding Historic Files

To update csv files:
1. navigate to `https://www.nasdaq.com/market-activity/stocks/<TICKER>/historical` replace `<TICKER>` with your choice. 
1. Download the historic data, unzip if needed. 
1. Rename the csv to the symbol and place in the `./tickerHistory` directory.
1. restart the app using `python app.py` from the root directory
