from dash import dcc, html
import pandas as pd
import dash_daq as daq

def create_layout(latest_date, five_years_ago, csv_files):
    return html.Div(className='main-container', children=[
        html.Div(className='top-row-container', children=[
            html.Button(
                html.I(className="fa fa-cog"),
                id='settings-button',
                className='settings-button',
                n_clicks=0
            ),
            html.Div(
                id='settings-modal',
                className='modal',
                style={'display': 'none'},
                children=[
                    html.Div(className='modal-content', children=[
                        html.Div(className='modal-header', children=[
                            html.H5('Settings'),
                            html.Button('×', id='close-settings', className='close-button')
                        ]),
                        html.Div(className='modal-body', children=[
                            html.Div(className='modal-section', children=[
                                html.Label('Graph Options:'),
                                dcc.Checklist(
                                    id='trace-toggle',
                                    options=[
                                        {'label': 'Volume', 'value': 'volume'},
                                        {'label': 'Open Price', 'value': 'open_price'},
                                        {'label': 'GME FTD', 'value': 'ftd'}
                                    ],
                                    value=['volume', 'open_price'],
                                    inline=True,
                                    className='trace-toggle'
                                ),
                            ]),
                            html.Div(className='modal-section color-picker-section', children=[
                                html.Div(className='color-picker-box', children=[
                                    html.Label('Static Chart Color:'),
                                    daq.ColorPicker(
                                        id='static-chart-color',
                                        label='Pick Color',
                                        value=dict(hex='#0000FF')
                                    ),
                                ]),
                                html.Div(className='color-picker-box', children=[
                                    html.Label('Overlay Color:'),
                                    daq.ColorPicker(
                                        id='overlay-color',
                                        label='Pick Color',
                                        value=dict(hex='#FF0000')
                                    ),
                                ]),
                            ]),
                            html.Div(className='modal-section color-picker-section', children=[
                                html.Div(className='color-picker-box', children=[
                                    html.Label('FTD Lines Color:'),
                                    daq.ColorPicker(
                                        id='ftd-lines-color',
                                        label='Pick Color',
                                        value=dict(hex='#00FF00')
                                    ),
                                ]),
                            ]),
                        ])
                    ])
                ]
            ),
            dcc.Dropdown(
                id='csv-dropdown',
                options=[{'label': f.replace('.csv', ''), 'value': f} for f in csv_files],
                value=csv_files[0],
                className='dropdown'
            ),
            html.Div(className='slider-container', children=[
                html.Div(className='slider-box', children=[
                    html.Label('X-axis Offset:', id='x-offset-label'),
                    dcc.Slider(id='x-offset-slider', min=-5*365, max=5*365, value=0, step=0.5, marks={i: str(i//365) + 'Y' for i in range(-5*365, 1, 5*365)}, updatemode='drag')
                ]),
                html.Div(className='slider-box', children=[
                    html.Label('X-Axis Scale Factor:', id='x-scale-label'),
                    dcc.Slider(id='x-scale-slider', min=0, max=10.0, value=1.0, step=0.001, marks={i: str(i) for i in range(0, 11)}, updatemode='drag')
                ]),
            ]),
            html.Div(className='slider-container', children=[
                html.Div(className='slider-box', children=[
                    html.Label('Y-Axis Offset:', id='y-offset-label'),
                    dcc.Slider(id='y-offset-slider', min=-200, max=50, value=0, step=1, marks={i: str(i) for i in range(-50, 51, 10)}, updatemode='drag')
                ]),
                html.Div(className='slider-box', children=[
                    html.Label('Y-Axis Scale Factor:', id='y-scale-label'),
                    dcc.Slider(id='y-scale-slider', min=0, max=10.0, value=1.0, step=0.001, marks={i: str(i) for i in range(0, 11)}, updatemode='drag')
                ]),
            ]),
            html.Div(className='date-picker-container', children=[
                html.Label('Use Custom Overlay Range:', className='toggle-label'),
                dcc.RadioItems(
                    id='date-range-toggle',
                    options=[{'label': 'No', 'value': 'no'}, {'label': 'Yes', 'value': 'yes'}],
                    value='no', labelStyle={'display': 'inline-block'}
                ),
                dcc.DatePickerRange(id='date-picker-range', start_date=five_years_ago, end_date=latest_date, display_format='MM-DD-YYYY'),
                html.Label('Custom Static Range', className='toggle-label'),
                dcc.DatePickerRange(id='historic-picker-range', start_date=five_years_ago, end_date=latest_date, display_format='MM-DD-YYYY')
            ]),
        ]),
        html.Button('Calculate Best Fit', id='calculate-best-fit-button', n_clicks=0, className='btn-calculate'),
        dcc.Loading(
            id="initial-loading",
            type="default",
            children=dcc.Graph(id='stock-graph')
        ),
        html.Div(className='log-slider-container', children=[
            html.Div(className='slider-box', children=[
                html.Label('Open Price Logarithmic Scale Factor:', id='log-scale-label'),
                dcc.Slider(id='log-scale-slider', min=0, max=100, value=0, step=1, marks={i: str(i) for i in range(101)}, updatemode='drag')
            ]),
        ]),
    ])
