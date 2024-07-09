import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html, Dash, Input, Output, State
from datetime import timedelta
import numpy as np
from scipy.optimize import minimize

# Load the data
file_path = "./Daily2020.csv"
df = pd.read_csv(file_path, parse_dates=['Date'])
df = df.sort_values('Date')

ftd_file_path = "./combined_gme_Data.csv"
ftd_df = pd.read_csv(ftd_file_path)
ftd_df['SETTLEMENT DATE'] = pd.to_datetime(ftd_df['SETTLEMENT DATE'], format='%Y%m%d')
ftd_df['SETTLEMENT DATE'] = ftd_df['SETTLEMENT DATE'].dt.strftime('%m/%d/%Y')
ftd_df['SETTLEMENT DATE'] = pd.to_datetime(ftd_df['SETTLEMENT DATE'], format='%m/%d/%Y')
ftd_df = ftd_df[ftd_df['QUANTITY (FAILS)'] > 150000]

# Calculate specific date ranges for the most recent three months
latest_date = df['Date'].max()
three_months_ago = latest_date - pd.Timedelta(days=90)
five_years_ago = latest_date - pd.Timedelta(days=5*365)

# Filter data for specific ranges
three_months_data = df[(df['Date'] >= three_months_ago) & (df['Date'] <= latest_date)]

external_stylesheets = ['./assets/styles.css']

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=external_stylesheets)

def app_layout(df, three_months_data, five_years_ago, latest_date, ftd_df):
    return html.Div(className='main-container', children=[
        html.Div(className='date-picker-container', id='date-picker-container', children=[
            html.Label('Overlay Custom Date Range:', className='toggle-label'),
            dcc.RadioItems(
                id='date-range-toggle',
                options=[
                    {'label': 'No', 'value': 'no'},
                    {'label': 'Yes', 'value': 'yes'}
                ],
                value='no',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=five_years_ago,
                end_date=latest_date,
                display_format='MM-DD-YYYY'
            ),
            html.Label('Custom Historic Data Range', className='toggle-label'),
            dcc.DatePickerRange(
                id='historic-picker-range',
                start_date=five_years_ago,
                end_date=latest_date,
                display_format='MM-DD-YYYY'
            )
        ]),
        html.Div(children=[
            html.Label('Toggle Traces:'),
            dcc.Checklist(
                id='trace-toggle',
                options=[
                    {'label': 'Show Volume', 'value': 'volume'},
                    {'label': 'Show Open Price', 'value': 'open_price'},
                    {'label': 'Show FTD', 'value': 'ftd'}  # Add this line
                ],
                value=['volume', 'open_price'],
                inline=True
            )
        ]),
        dcc.Graph(id='stock-graph'),
        html.Button('Calculate Best Fit', id='calculate-best-fit-button', n_clicks=0, className='btn-calculate'),
        html.Div(className='slider-container', children=[
            html.Div(className='slider-box', children=[
                html.Label('Move Slider:', id='move-label'),
                dcc.Slider(
                    id='move-slider',
                    min=-5*365,  # Extend the range to allow moving up to 5 years back (in days)
                    max=5*365,
                    value=0,
                    step=0.5,
                    marks={i: str(i//365) + 'Y' for i in range(-5*365, 1, 5*365)},
                    updatemode='drag'
                ),
            ]),
            html.Div(className='slider-box', children=[
                html.Label('Y-Axis Offset:', id='y-offset-label'),
                dcc.Slider(
                    id='y-offset-slider',
                    min=-200,  # Adjust the range as necessary
                    max=50,  # Adjust the range as necessary
                    value=0,
                    step=1,
                    marks={i: str(i) for i in range(-50, 51, 10)},
                    updatemode='drag'
                ),
            ]),
        ]),
        html.Div(className='slider-container', children=[
            html.Div(className='slider-box', children=[
                html.Label('X-Axis Scale Factor:', id='x-scale-label'),
                dcc.Slider(
                    id='x-scale-slider',
                    min=0,
                    max=10.0,
                    value=1.0,
                    step=0.001,
                    marks={i: str(i) for i in range(0, 11)},
                    updatemode='drag'
                ),
            ]),
            html.Div(className='slider-box', children=[
                html.Label('Y-Axis Scale Factor:', id='y-scale-label'),
                dcc.Slider(
                    id='y-scale-slider',
                    min=0,
                    max=10.0,
                    value=1.0,
                    step=0.001,
                    marks={i: str(i) for i in range(0,11)},
                    updatemode='drag'
                ),
            ]),
        ]),
        html.Div(className='slider-container', children=[
            html.Div(className='slider-box', children=[
                html.Label('Open Price Logarithmic Scale Factor:', id='log-scale-label'),
                dcc.Slider(
                    id='log-scale-slider',
                    min=0,
                    max=100,
                    value=0,
                    step=1,
                    marks={i: str(i) for i in range(101)},
                    updatemode='drag'
                ),
            ]),
        ]),
    ])

def register_callbacks(app, df, three_months_data, ftd_df):

    @app.callback(
        Output('stock-graph', 'figure'),
        [
            Input('date-range-toggle', 'value'),
            Input('date-picker-range', 'start_date'),
            Input('date-picker-range', 'end_date'),
            Input('historic-picker-range', 'start_date'),
            Input('historic-picker-range', 'end_date'),
            Input('move-slider', 'value'),
            Input('y-scale-slider', 'value'),
            Input('x-scale-slider', 'value'),
            Input('y-offset-slider', 'value'),
            Input('log-scale-slider', 'value'),
            Input('trace-toggle', 'value'),
            State('stock-graph', 'relayoutData')
        ]
    )
    def update_graph(use_date_range, start_date, end_date, five_year_start, five_year_end, move, y_scale, x_scale, y_offset, log_scale, trace_toggle, relayoutData):
        # Custom Historic data (static)
        five_year_data = df[(df['Date'] >= five_year_start) & (df['Date'] <= five_year_end)]
        trace_five_year = go.Scatter(
            x=five_year_data['Date'],
            y=five_year_data['Open'],
            mode='lines',
            name='Historic Data Range',
            text=five_year_data['Date'].dt.strftime('%b %d, %Y'),
            hovertemplate='%{text}, %{y:.2f}',
            line=dict(color='blue')  # Set the color to blue
            
        )
        
        volume_five_year = go.Scatter(
            x=five_year_data['Date'],
            y=five_year_data['Volume'],
            name='Volume',
            marker=dict(color='rgba(50, 50, 150, 0.5)'),
            yaxis='y2',
            mode='lines'
        )

        if use_date_range == 'yes':
            # Custom date range data
            custom_date_range_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            overlay_data = custom_date_range_data.copy()
        else:
            # Three-month data (always the most recent three months, but moved and scaled)
            overlay_data = three_months_data.copy()

        overlay_data['Date'] = overlay_data['Date'] + timedelta(days=move)
        
        # Scale the x-axis (date range) of the overlay data
        date_range = overlay_data['Date'].max() - overlay_data['Date'].min()
        if date_range.total_seconds() != 0:
            scaled_date_range = date_range * x_scale
            overlay_data['Date'] = overlay_data['Date'].min() + (overlay_data['Date'] - overlay_data['Date'].min()) / date_range * scaled_date_range

        # Apply logarithmic scaling to the open price
        overlay_log_scaled_data = np.log(overlay_data['Open']) * log_scale if log_scale > 0 else overlay_data['Open']
        
        # Scale and offset the y-axis (price range) of the overlay data
        overlay_scaled_data = overlay_log_scaled_data * y_scale + y_offset

        # Use the original date for hover text
        trace_overlay = go.Scatter(
            x=overlay_data['Date'],
            y=overlay_scaled_data,
            mode='lines',
            name='Overlay Data',
            text=overlay_data['Date'].dt.strftime('%b %d, %Y'),  # Set the hover text to the original dates
            hovertemplate='%{text}, %{y:.2f}'
        )

        volume_overlay = go.Scatter(
            x=overlay_data['Date'],
            y=overlay_data['Volume'],
            name='Overlay Volume',
            marker=dict(color='rgba(150, 50, 50, 0.5)'),
            yaxis='y2',
            mode='lines'
        )

        # Create lines for FTD data
        ftd_lines = []
        for _, row in ftd_df.iterrows():
            start_date = row['SETTLEMENT DATE']
            end_date = start_date + pd.Timedelta(days=35)
            ftd_lines.append(go.Scatter(
                x=[start_date, end_date],
                y=[row['PRICE'], row['PRICE']],
                mode='lines',
                name='FTD Data',
                line=dict(color='red', width=2),
                hovertext=f"FTD from {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}, Price: {row['PRICE']:.2f}",
                hoverinfo='text'
            ))

        data = []
        
        if 'ftd' in trace_toggle:
            data.extend(ftd_lines)

        if 'open_price' in trace_toggle:
            data.append(trace_five_year)
            data.append(trace_overlay)
        if 'volume' in trace_toggle:
            data.append(volume_five_year)
            data.append(volume_overlay)

        layout = go.Layout(
            title='Stock Data: 5-Year and Overlay',
            xaxis={'title': 'Date'},
            yaxis={'title': 'Open Price'},
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            showlegend=True,
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font={'color': '#7FDBFF'},
        )

        # Preserve the current zoom/axis range if available
        if relayoutData and 'xaxis.range[0]' in relayoutData:
            layout['xaxis']['range'] = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
        if relayoutData and 'yaxis.range[0]' in relayoutData:
            layout['yaxis']['range'] = [relayoutData['yaxis.range[0]'], relayoutData['yaxis.range[1]']]
        if relayoutData and 'yaxis2.range[0]' in relayoutData:
            layout['yaxis2']['range'] = [relayoutData['yaxis2.range[0]'], relayoutData['yaxis2.range[1]']]

        return {
            'data': data,
            'layout': layout
        }

    @app.callback(
        Output('move-label', 'children'),
        [Input('move-slider', 'value')]
    )
    def update_move_label(value):
        return f'Move Slider: {value} days'

    @app.callback(
        Output('y-scale-label', 'children'),
        [Input('y-scale-slider', 'value')]
    )
    def update_y_scale_label(value):
        return f'Y-Axis Scale Factor: {value}'

    @app.callback(
        Output('x-scale-label', 'children'),
        [Input('x-scale-slider', 'value')]
    )
    def update_x_scale_label(value):
        return f'X-Axis Scale Factor: {value}'

    @app.callback(
        Output('y-offset-label', 'children'),
        [Input('y-offset-slider', 'value')]
    )
    def update_y_offset_label(value):
        return f'Y-Axis Offset: {value}'

    @app.callback(
        Output('log-scale-label', 'children'),
        [Input('log-scale-slider', 'value')]
    )
    def update_log_scale_label(value):
        return f'Open Price Logarithmic Scale Factor: {value}'

    def calculate_fit(params, overlay_data, df):
        move, y_scale, x_scale, y_offset, log_scale = params

        # Apply the transformations
        overlay_data_moved = overlay_data.copy()
        overlay_data_moved['Date'] = overlay_data_moved['Date'] + timedelta(days=move)
        
        date_range = overlay_data_moved['Date'].max() - overlay_data_moved['Date'].min()
        if date_range.total_seconds() != 0:
            scaled_date_range = date_range * x_scale
            overlay_data_moved['Date'] = overlay_data_moved['Date'].min() + (overlay_data_moved['Date'] - overlay_data_moved['Date'].min()) / date_range * scaled_date_range

        overlay_log_scaled_data = np.log(overlay_data_moved['Open']) * log_scale if log_scale > 0 else overlay_data_moved['Open']
        overlay_scaled_data = overlay_log_scaled_data * y_scale + y_offset

        # Convert datetime64 to int64 for interpolation
        interpolated_five_year = np.interp(overlay_data_moved['Date'].astype('int64') // 10**9, df['Date'].astype('int64') // 10**9, df['Open'])
        diff = interpolated_five_year - overlay_scaled_data
        return np.sum(diff**2)

    @app.callback(
        Output('move-slider', 'value'),
        Output('y-scale-slider', 'value'),
        Output('x-scale-slider', 'value'),
        Output('y-offset-slider', 'value'),
        Output('log-scale-slider', 'value'),
        Input('calculate-best-fit-button', 'n_clicks'),
        State('move-slider', 'value'),
        State('y-scale-slider', 'value'),
        State('x-scale-slider', 'value'),
        State('y-offset-slider', 'value'),
        State('log-scale-slider', 'value'),
        State('date-range-toggle', 'value'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date')
    )
    def calculate_best_fit(n_clicks, move, y_scale, x_scale, y_offset, log_scale, use_date_range, start_date, end_date):
        if n_clicks == 0:
            return move, y_scale, x_scale, y_offset, log_scale

        if use_date_range == 'yes':
            overlay_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        else:
            overlay_data = three_months_data.copy()

        initial_params = [move, y_scale, x_scale, y_offset, log_scale]
        result = minimize(calculate_fit, initial_params, args=(overlay_data, df), method='Nelder-Mead')
        
        return result.x[0], result.x[1], result.x[2], result.x[3], result.x[4]



# Set the layout from the separate layout file
app.layout = app_layout(df, three_months_data, five_years_ago, latest_date, ftd_df)

# Register callbacks from the separate layout file
register_callbacks(app, df, three_months_data, ftd_df)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
