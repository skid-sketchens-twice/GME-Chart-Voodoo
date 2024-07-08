import pandas as pd
from dash import Dash
from layout import app_layout, register_callbacks  # Import layout and callbacks

# Load the data
file_path = "./Daily2020.csv"
df = pd.read_csv(file_path, parse_dates=['Date'])
df = df.sort_values('Date')

# Calculate specific date ranges for the most recent three months
latest_date = df['Date'].max()
three_months_ago = latest_date - pd.Timedelta(days=90)
five_years_ago = latest_date - pd.Timedelta(days=5*365)

# Filter data for specific ranges
three_months_data = df[(df['Date'] >= three_months_ago) & (df['Date'] <= latest_date)]

external_stylesheets = [
    './assets/styles.css'  # Ensure the correct path to your CSS file
]

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Set the layout from the separate layout file
app.layout = app_layout(df, three_months_data, five_years_ago, latest_date)

# Register callbacks from the separate layout file
register_callbacks(app, df, three_months_data)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
