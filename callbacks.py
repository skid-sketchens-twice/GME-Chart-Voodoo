from dash import Input, Output, State, callback_context
from utils import update_graph, calculate_best_fit
import pandas as pd

def register_callbacks(app, df, ftd_df, three_months_data):
    @app.callback(
        [
            Output('date-picker-range', 'start_date'),
            Output('date-picker-range', 'end_date'),
            Output('historic-picker-range', 'start_date'),
            Output('historic-picker-range', 'end_date'),
            Output('stock-graph', 'figure'),
        ],
        [
            Input('csv-dropdown', 'value'),
            Input('date-range-toggle', 'value'),
            Input('date-picker-range', 'start_date'),
            Input('date-picker-range', 'end_date'),
            Input('historic-picker-range', 'start_date'),
            Input('historic-picker-range', 'end_date'),
            Input('x-offset-slider', 'value'),
            Input('y-scale-slider', 'value'),
            Input('x-scale-slider', 'value'),
            Input('y-offset-slider', 'value'),
            Input('log-scale-slider', 'value'),
            Input('trace-toggle', 'value'),
            Input('static-chart-color', 'value'),
            Input('overlay-color', 'value'),
            Input('ftd-lines-color', 'value'),
            State('stock-graph', 'relayoutData')
        ]
    )
    def update_graph_callback(csv_file, use_date_range, start_date, end_date, five_year_start, five_year_end, x_offset, y_scale, x_scale, y_offset, log_scale, trace_toggle, static_chart_color, overlay_color, ftd_lines_color, relayoutData):
        # Get the context to identify which input triggered the callback
        ctx = callback_context
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        # Update the graph if csv file is changed or color pickers are used
        if csv_file is None:
            return start_date, end_date, five_year_start, five_year_end, {
                'data': [],
                'layout': {
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Open Price'},
                    'yaxis2': {'title': 'Volume', 'overlaying': 'y', 'side': 'right', 'showgrid': True},
                    'showlegend': True,
                    'plot_bgcolor': '#1e1e1e',
                    'paper_bgcolor': '#1e1e1e',
                    'font': {'color': '#7FDBFF'},
                    'height': 550,
                    'xaxis_rangeslider': {'visible': True}
                }
            }

        # Check if color picker triggered the callback
        if trigger in ['static-chart-color', 'overlay-color', 'ftd-lines-color']:
            figure = update_graph(
                df, ftd_df, csv_file, use_date_range, start_date, end_date,
                five_year_start, five_year_end, x_offset, y_scale, x_scale,
                y_offset, log_scale, trace_toggle, relayoutData,
                static_chart_color['hex'], overlay_color['hex'], ftd_lines_color['hex']
            )
            return start_date, end_date, five_year_start, five_year_end, figure

        figure = update_graph(
            df, ftd_df, csv_file, use_date_range, start_date, end_date,
            five_year_start, five_year_end, x_offset, y_scale, x_scale,
            y_offset, log_scale, trace_toggle, relayoutData
        )

        if use_date_range == 'yes' and start_date and end_date:
            figure['layout']['xaxis']['range'] = [start_date, end_date]
        elif five_year_start and five_year_end:
            figure['layout']['xaxis']['range'] = [five_year_start, five_year_end]
        else:
            figure['layout']['xaxis']['range'] = [df['Date'].min(), df['Date'].max()]

        return start_date, end_date, five_year_start, five_year_end, figure

    @app.callback(
        Output('settings-modal', 'style'),
        [Input('settings-button', 'n_clicks'), Input('close-settings', 'n_clicks')],
        [State('settings-modal', 'style')]
    )
    def toggle_modal(settings_n_clicks, close_n_clicks, style):
        if settings_n_clicks or close_n_clicks:
            if style and style['display'] == 'block':
                return {'display': 'none'}
            else:
                return {'display': 'block'}
        return style

    @app.callback(Output('x-offset-label', 'children'), [Input('x-offset-slider', 'value')])
    def update_x_offset_label(value):
        return f'X-Axis Offset: {value} days'

    @app.callback(Output('y-scale-label', 'children'), [Input('y-scale-slider', 'value')])
    def update_y_scale_label(value):
        return f'Y-Axis Scale Factor: {value}'

    @app.callback(Output('x-scale-label', 'children'), [Input('x-scale-slider', 'value')])
    def update_x_scale_label(value):
        return f'X-Axis Scale Factor: {value}'

    @app.callback(Output('y-offset-label', 'children'), [Input('y-offset-slider', 'value')])
    def update_y_offset_label(value):
        return f'Y-Axis Offset: {value}'

    @app.callback(Output('log-scale-label', 'children'), [Input('log-scale-slider', 'value')])
    def update_log_scale_label(value):
        return f'Open Price Logarithmic Scale Factor: {value}'

    @app.callback(
        Output('x-offset-slider', 'value'),
        Output('y-scale-slider', 'value'),
        Output('x-scale-slider', 'value'),
        Output('y-offset-slider', 'value'),
        Output('log-scale-slider', 'value'),
        Input('calculate-best-fit-button', 'n_clicks'),
        State('x-offset-slider', 'value'),
        State('y-scale-slider', 'value'),
        State('x-scale-slider', 'value'),
        State('y-offset-slider', 'value'),
        State('log-scale-slider', 'value'),
        State('date-range-toggle', 'value'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date')
    )
    def calculate_best_fit_callback(n_clicks, x_offset, y_scale, x_scale, y_offset, log_scale, use_date_range, start_date, end_date):
        return calculate_best_fit(df, three_months_data, n_clicks, x_offset, y_scale, x_scale, y_offset, log_scale, use_date_range, start_date, end_date)
