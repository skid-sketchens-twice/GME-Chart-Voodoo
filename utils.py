import pandas as pd
import numpy as np
from datetime import timedelta
from scipy.optimize import minimize
import plotly.graph_objs as go

def load_and_standardize_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])
    if 'Close/Last' in df.columns:
        df.rename(columns={'Close/Last': 'Close'}, inplace=True)
    if 'Adj Close' not in df.columns:
        df['Adj Close'] = df['Close']
    df['Open'] = df['Open'].replace('[\$,]', '', regex=True).astype(float)
    return df.sort_values('Date')

def calculate_fit(params, overlay_data, df):
    move, y_scale, x_scale, y_offset, log_scale = map(float, params)
    overlay_data_moved = overlay_data.copy()
    overlay_data_moved['Date'] += timedelta(days=move)
    
    date_range = overlay_data_moved['Date'].max() - overlay_data_moved['Date'].min()
    if date_range.total_seconds() != 0:
        scaled_date_range = date_range * x_scale
        overlay_data_moved['Date'] = overlay_data_moved['Date'].min() + (overlay_data_moved['Date'] - overlay_data_moved['Date'].min()) / date_range * scaled_date_range

    overlay_log_scaled_data = np.log(overlay_data_moved['Open']) * log_scale if log_scale > 0 else overlay_data_moved['Open']
    overlay_scaled_data = overlay_log_scaled_data * y_scale + y_offset

    interpolated_five_year = np.interp(overlay_data_moved['Date'].astype('int64') // 10**9, df['Date'].astype('int64') // 10**9, df['Open'])
    diff = interpolated_five_year - overlay_scaled_data
    return np.sum(diff**2)

def update_graph(
    df, ftd_df, csv_file, use_date_range, start_date, end_date, 
    five_year_start, five_year_end, move, y_scale, x_scale, 
    y_offset, log_scale, trace_toggle, relayoutData,
    static_chart_color='#0000FF', overlay_color='#FF0000', ftd_lines_color='#00FF00'
):
    df = load_and_standardize_data(f'./tickerHistory/{csv_file}')
    latest_date = df['Date'].max()
    three_months_ago = latest_date - pd.Timedelta(days=90)
    five_years_ago = latest_date - pd.Timedelta(days=5*365)
    three_months_data = df[(df['Date'] >= three_months_ago) & (df['Date'] <= latest_date)]

    if start_date is None:
        start_date = three_months_ago
    if end_date is None:
        end_date = latest_date
    if five_year_start is None:
        five_year_start = five_years_ago
    if five_year_end is None:
        five_year_end = latest_date

    move = float(move)
    y_scale = float(y_scale)
    x_scale = float(x_scale)
    y_offset = float(y_offset)
    log_scale = float(log_scale)

    five_year_data = df[(df['Date'] >= five_year_start) & (df['Date'] <= five_year_end)]
    trace_five_year = go.Scatter(
        x=five_year_data['Date'], y=five_year_data['Open'], mode='lines', name='Historic Data',
        text=five_year_data['Date'].dt.strftime('%b %d, %Y'), hovertemplate='%{text}, %{y:.2f}', line=dict(color=static_chart_color)
    )
    volume_five_year = go.Bar(
        x=five_year_data['Date'], y=five_year_data['Volume'], name='Volume', marker=dict(color='rgba(50, 50, 150, 0.5)'),
        yaxis='y2'
    )

    overlay_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)] if use_date_range == 'yes' else three_months_data.copy()
    overlay_data['Original Date'] = overlay_data['Date']
    overlay_data['Original Open'] = overlay_data['Open']
    overlay_data['Original Volume'] = overlay_data['Volume']
    overlay_data['Date'] += timedelta(days=move)

    date_range = overlay_data['Date'].max() - overlay_data['Date'].min()
    if date_range.total_seconds() != 0:
        scaled_date_range = date_range * x_scale
        overlay_data['Date'] = overlay_data['Date'].min() + (overlay_data['Date'] - overlay_data['Date'].min()) / date_range * scaled_date_range

    overlay_log_scaled_data = np.log(overlay_data['Open']) * log_scale if log_scale > 0 else overlay_data['Open']
    overlay_scaled_data = overlay_log_scaled_data * y_scale + y_offset
    overlay_scaled_volume = overlay_data['Volume'] * y_scale

    trace_overlay = go.Scatter(
        x=overlay_data['Date'], y=overlay_scaled_data, mode='lines', name='Overlay Data',
        text=overlay_data['Original Date'].dt.strftime('%b %d, %Y'), hovertemplate='%{text}, %{y:.2f} (Original: %{customdata[0]:.2f})',
        customdata=np.stack((overlay_data['Original Open'],), axis=-1), line=dict(color=overlay_color)
    )
    volume_overlay = go.Bar(
        x=overlay_data['Date'], y=overlay_scaled_volume, name='Overlay Volume',
        marker=dict(color='rgba(150, 50, 50, 0.5)'), yaxis='y2',
        text=overlay_data['Original Date'].dt.strftime('%b %d, %Y'), hovertemplate='%{text}, %{y} (Original: %{customdata[0]})',
        customdata=np.stack((overlay_data['Original Volume'].apply(format_volume),), axis=-1)
    )

    ftd_lines = [
        go.Scatter(
            x=[row['SETTLEMENT DATE'], row['SETTLEMENT DATE'] + pd.Timedelta(days=35)],
            y=[row['PRICE'], row['PRICE']],
            mode='lines',
            name=row['SETTLEMENT DATE'].strftime('%Y-%m-%d'),
            line=dict(color=ftd_lines_color, width=1),
            hovertext=f"FTD from {row['SETTLEMENT DATE'].strftime('%b %d, %Y')} to {(row['SETTLEMENT DATE'] + pd.Timedelta(days=35)).strftime('%b %d, %Y')}, Price: {row['PRICE']:.2f}",
            hoverinfo='text'
        )
        for _, row in ftd_df.iterrows()
    ]

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
        title='Stock Data: Static and Overlay',
        xaxis={'title': 'Date', 'range': [df['Date'].min(), df['Date'].max()]},
        yaxis={'title': 'Open Price'},
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=True),
        showlegend=True,
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font={'color': '#7FDBFF'},
        height=550,
        xaxis_rangeslider={'visible': True}
    )

    if relayoutData and 'xaxis.range[0]' in relayoutData:
        layout['xaxis']['range'] = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
    else:
        if use_date_range == 'yes':
            layout['xaxis']['range'] = [start_date, end_date]
        else:
            layout['xaxis']['range'] = [five_year_start, five_year_end]

    if relayoutData and 'yaxis.range[0]' in relayoutData:
        layout['yaxis']['range'] = [relayoutData['yaxis.range[0]'], relayoutData['yaxis.range[1]']]
    if relayoutData and 'yaxis2.range[0]' in relayoutData:
        layout['yaxis2']['range'] = [relayoutData['yaxis2.range[0]'], relayoutData['yaxis2.range[1]']]

    return {'data': data, 'layout': layout}


def calculate_best_fit(df, three_months_data, n_clicks, move, y_scale, x_scale, y_offset, log_scale, use_date_range, start_date, end_date):
    if n_clicks == 0:
        return move, y_scale, x_scale, y_offset, log_scale

    move = float(move)
    y_scale = float(y_scale)
    x_scale = float(x_scale)
    y_offset = float(y_offset)
    log_scale = float(log_scale)

    overlay_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)] if use_date_range == 'yes' else three_months_data.copy()
    initial_params = [move, y_scale, x_scale, y_offset, log_scale]
    result = minimize(calculate_fit, initial_params, args=(overlay_data, df), method='Nelder-Mead')
    
    return result.x[0], result.x[1], result.x[2], result.x[3], result.x[4]

def format_volume(volume):
    if volume >= 1e9:
        return f'{volume / 1e9:.2f}B'
    elif volume >= 1e6:
        return f'{volume / 1e6:.2f}M'
    else:
        return str(volume)
