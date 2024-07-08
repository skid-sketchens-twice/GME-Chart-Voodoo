import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output, State
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize

# Load the data
file_path = "./Daily2020.csv"
df = pd.read_csv(file_path, parse_dates=['Date'])
df = df.sort_values('Date')

# Calculate specific date ranges for the most recent three months
latest_date = df['Date'].max()
three_months_ago = latest_date - timedelta(days=90)
five_years_ago = latest_date - timedelta(days=5*365)

# Filter data for specific ranges
three_months_data = df[(df['Date'] >= three_months_ago) & (df['Date'] <= latest_date)]

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div(style={'backgroundColor': '#1e1e1e', 'color': '#7FDBFF', 'padding': '20px'}, children=[
    dcc.Graph(id='stock-graph'),
    html.Div(style={'padding': '20px', 'display': 'flex', 'justify-content': 'space-between'}, children=[
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label('3-Month Move Slider:', id='month-move-label', style={'font-weight': 'bold'}),
            dcc.Slider(
                id='month-move-slider',
                min=-5*365,  # Extend the range to allow moving up to 5 years back (in days)
                max=0,
                value=-5*365 // 2,
                step=0.001,
                marks={i: str(i//365) + 'Y' for i in range(-5*365, 1, 365)},
                updatemode='drag'
            ),
        ]),
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label('3-Month Y-Axis Offset:', id='month-y-offset-label', style={'font-weight': 'bold'}),
            dcc.Slider(
                id='month-y-offset-slider',
                min=-50,  # Adjust the range as necessary
                max=50,  # Adjust the range as necessary
                value=0,
                step=10,
                marks={i: str(i) for i in range(-50, 51, 10)},
                updatemode='drag'
            ),
        ]),
    ]),
    html.Div(style={'padding': '20px', 'display': 'flex', 'justify-content': 'space-between'}, children=[
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label('3-Month X-Axis Scale Factor:', id='month-x-scale-label', style={'font-weight': 'bold'}),
            dcc.Slider(
                id='month-x-scale-slider',
                min=-5.0,
                max=5.0,
                value=1.0,
                step=0.001,
                marks={i: str(i) for i in range(-5, 6)},
                updatemode='drag'
            ),
        ]),
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label('3-Month Y-Axis Scale Factor:', id='month-y-scale-label', style={'font-weight': 'bold'}),
            dcc.Slider(
                id='month-y-scale-slider',
                min=-5.0,
                max=5.0,
                value=1.0,
                step=0.001,
                marks={i: str(i) for i in range(-5, 6)},
                updatemode='drag'
            ),
        ]),
    ]),
    html.Div(style={'padding': '20px', 'display': 'flex', 'justify-content': 'space-between'}, children=[
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label('Open Price Logarithmic Scale Factor:', id='log-scale-label', style={'font-weight': 'bold'}),
            dcc.Slider(
                id='log-scale-slider',
                min=0,
                max=20,
                value=0,
                step=0.25,
                marks={i: str(i) for i in range(21)},
                updatemode='drag'
            ),
        ]),
    ]),
    html.Button('Calculate Best Fit', id='calculate-best-fit-button', n_clicks=0, style={'margin': '20px', 'background-color': '#007BFF', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'cursor': 'pointer', 'font-weight': 'bold'}),
])


# Callback to update the graph based on the sliders
@app.callback(
    Output('stock-graph', 'figure'),
    [
        Input('month-move-slider', 'value'),
        Input('month-y-scale-slider', 'value'),
        Input('month-x-scale-slider', 'value'),
        Input('month-y-offset-slider', 'value'),
        Input('log-scale-slider', 'value')
    ]
)
def update_graph(month_move, month_y_scale, month_x_scale, month_y_offset, log_scale):
    # Five-year data (static)
    trace_five_year = go.Scatter(x=df['Date'], y=df['Open'], mode='lines', name='5-Year Data')

    # Three-month data (always the most recent three months, but moved and scaled)
    three_months_data_moved = three_months_data.copy()
    three_months_data_moved['Date'] = three_months_data_moved['Date'] + timedelta(days=month_move)
    
    # Scale the x-axis (date range) of the three-month data
    date_range = three_months_data_moved['Date'].max() - three_months_data_moved['Date'].min()
    if date_range.total_seconds() != 0:
        scaled_date_range = date_range * month_x_scale
        three_months_data_moved['Date'] = three_months_data_moved['Date'].min() + (three_months_data_moved['Date'] - three_months_data_moved['Date'].min()) / date_range * scaled_date_range

    # Apply logarithmic scaling to the open price
    three_months_log_scaled_data = np.log(three_months_data_moved['Open']) * log_scale if log_scale > 0 else three_months_data_moved['Open']
    
    # Scale and offset the y-axis (price range) of the three-month data
    three_months_scaled_data = three_months_log_scaled_data * month_y_scale + month_y_offset
    trace_three_months = go.Scatter(
        x=three_months_data_moved['Date'],
        y=three_months_scaled_data,
        mode='lines',
        name='3-Month Data'
    )

    return {
        'data': [trace_five_year, trace_three_months],
        'layout': go.Layout(
            title='Stock Data: 5-Year and 3-Month Overlay',
            xaxis={'title': 'Date'},
            yaxis={'title': 'Open Price'},
            showlegend=True,
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font={'color': '#7FDBFF'}
        )
    }

@app.callback(
    Output('month-move-label', 'children'),
    [Input('month-move-slider', 'value')]
)
def update_month_move_label(value):
    return f'3-Month Move Slider: {value} days'

@app.callback(
    Output('month-y-scale-label', 'children'),
    [Input('month-y-scale-slider', 'value')]
)
def update_month_y_scale_label(value):
    return f'3-Month Y-Axis Scale Factor: {value}'

@app.callback(
    Output('month-x-scale-label', 'children'),
    [Input('month-x-scale-slider', 'value')]
)
def update_month_x_scale_label(value):
    return f'3-Month X-Axis Scale Factor: {value}'

@app.callback(
    Output('month-y-offset-label', 'children'),
    [Input('month-y-offset-slider', 'value')]
)
def update_month_y_offset_label(value):
    return f'3-Month Y-Axis Offset: {value}'

@app.callback(
    Output('log-scale-label', 'children'),
    [Input('log-scale-slider', 'value')]
)
def update_log_scale_label(value):
    return f'Open Price Logarithmic Scale Factor: {value}'

def calculate_fit(params, three_months_data, df):
    month_move, month_y_scale, month_x_scale, month_y_offset, log_scale = params

    # Apply the transformations
    three_months_data_moved = three_months_data.copy()
    three_months_data_moved['Date'] = three_months_data_moved['Date'] + timedelta(days=month_move)
    
    date_range = three_months_data_moved['Date'].max() - three_months_data_moved['Date'].min()
    if date_range.total_seconds() != 0:
        scaled_date_range = date_range * month_x_scale
        three_months_data_moved['Date'] = three_months_data_moved['Date'].min() + (three_months_data_moved['Date'] - three_months_data_moved['Date'].min()) / date_range * scaled_date_range

    three_months_log_scaled_data = np.log(three_months_data_moved['Open']) * log_scale if log_scale > 0 else three_months_data_moved['Open']
    three_months_scaled_data = three_months_log_scaled_data * month_y_scale + month_y_offset

    # Convert datetime64 to int64 for interpolation
    interpolated_five_year = np.interp(three_months_data_moved['Date'].astype('int64') // 10**9, df['Date'].astype('int64') // 10**9, df['Open'])
    diff = interpolated_five_year - three_months_scaled_data
    return np.sum(diff**2)

@app.callback(
    Output('month-move-slider', 'value'),
    Output('month-y-scale-slider', 'value'),
    Output('month-x-scale-slider', 'value'),
    Output('month-y-offset-slider', 'value'),
    Output('log-scale-slider', 'value'),
    Input('calculate-best-fit-button', 'n_clicks'),
    State('month-move-slider', 'value'),
    State('month-y-scale-slider', 'value'),
    State('month-x-scale-slider', 'value'),
    State('month-y-offset-slider', 'value'),
    State('log-scale-slider', 'value')
)
def calculate_best_fit(n_clicks, month_move, month_y_scale, month_x_scale, month_y_offset, log_scale):
    if n_clicks == 0:
        return month_move, month_y_scale, month_x_scale, month_y_offset, log_scale

    initial_params = [month_move, month_y_scale, month_x_scale, month_y_offset, log_scale]
    result = minimize(calculate_fit, initial_params, args=(three_months_data, df), method='Nelder-Mead')
    
    return result.x[0], result.x[1], result.x[2], result.x[3], result.x[4]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
