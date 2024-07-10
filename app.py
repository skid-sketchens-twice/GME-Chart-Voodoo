from dash import dcc, html, Dash
import os
from dash_extensions import Lottie  # Import Lottie for loading animations
from utils import load_and_standardize_data
from callbacks import register_callbacks
from layout import create_layout
import pandas as pd

# List CSV files in the directory
csv_files = [f for f in os.listdir('./tickerHistory/') if f.endswith('.csv')]
if 'GME.csv' in csv_files:
    csv_files.remove('GME.csv')
    csv_files.insert(0, 'GME.csv')

initial_file = f'./tickerHistory/{csv_files[0]}'
df = load_and_standardize_data(initial_file)
latest_date = df['Date'].max()
three_months_ago = latest_date - pd.Timedelta(days=90)
five_years_ago = latest_date - pd.Timedelta(days=5*365)
three_months_data = df[(df['Date'] >= three_months_ago) & (df['Date'] <= latest_date)]
ftd_df = pd.read_csv("./ftd_data/GME_FTD.csv")
ftd_df['SETTLEMENT DATE'] = pd.to_datetime(ftd_df['SETTLEMENT DATE'], format='%Y%m%d')
ftd_df = ftd_df[ftd_df['QUANTITY (FAILS)'] > 150000]

# Initialize the Dash app
external_stylesheets = [
    './assets/styles.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'  # Font Awesome for gear icon
]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Set the layout
app.layout = create_layout(latest_date, five_years_ago, csv_files)

# Register callbacks
register_callbacks(app, df, ftd_df, three_months_data)

if __name__ == '__main__':
    app.run_server(debug=True)
