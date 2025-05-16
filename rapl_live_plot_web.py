import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import os

csv_file = "rapl_power_log.csv"

app = dash.Dash(__name__)
app.title = "Live RAPL Power Monitor"

app.layout = html.Div([
    html.H1("Live RAPL Power Monitor", style={"textAlign": "center"}),

    dcc.Graph(id='live-graph', config={'displayModeBar': True}),

    html.Div(id='slider-container', style={"marginTop": "20px"}),

    html.Div(id='power-summary', style={"marginTop": "20px"}),

    html.Button("Pause", id='pause-button', n_clicks=0, style={"marginTop": "20px"}),

    dcc.Store(id='pause-state', data=False),

    dcc.Store(id='df-store'),

    dcc.Interval(
        id='interval-component',
        interval=1000,
        n_intervals=0
    )
], style={"margin": "20px"})


@app.callback(
    Output('pause-state', 'data'),
    Output('pause-button', 'children'),
    Input('pause-button', 'n_clicks'),
    State('pause-state', 'data'),
    prevent_initial_call=True
)
def toggle_pause(n_clicks, is_paused):
    new_state = not is_paused
    button_label = "Resume" if new_state else "Pause"
    return new_state, button_label


@app.callback(
    Output('df-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('pause-state', 'data'),
)
def update_data_store(n, is_paused):
    if is_paused or not os.path.exists(csv_file):
        raise dash.exceptions.PreventUpdate

    try:
        df = pd.read_csv(csv_file)
        if df.shape[0] == 0:
            raise dash.exceptions.PreventUpdate

        if not pd.api.types.is_string_dtype(df['Timestamp']):
            df['Timestamp'] = pd.to_datetime(df['Timestamp']).astype(str)

        return df.to_dict('records')

    except Exception as e:
        print(f"Error reading CSV: {e}")
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output('slider-container', 'children'),
    Input('df-store', 'data')
)
def update_slider(data):
    if not data:
        return html.Div()

    df = pd.DataFrame(data)
    n = len(df)

    timestamps = pd.to_datetime(df['Timestamp'])

    step = max(1, n // 10)
    marks = {}
    for i in range(0, n, step):
        ts = timestamps.iloc[i]
        marks[i] = ts.strftime('%H:%M:%S')

    marks[n - 1] = timestamps.iloc[-1].strftime('%H:%M:%S')

    slider = dcc.RangeSlider(
        id='time-range-slider',
        min=0,
        max=n - 1,
        value=[0, n - 1],
        marks=marks,
        tooltip={"placement": "bottom", "always_visible": True},
        allowCross=False
    )
    return slider


@app.callback(
    Output('live-graph', 'figure'),
    Output('power-summary', 'children'),
    Input('time-range-slider', 'value'),
    State('df-store', 'data'),
    State('pause-state', 'data')
)
def update_graph(time_range, data, is_paused):
    if is_paused or not data:
        raise dash.exceptions.PreventUpdate

    df = pd.DataFrame(data)
    if df.shape[0] == 0:
        return go.Figure(), html.Div("CSV is empty.")

    start_idx, end_idx = time_range
    df_filtered = df.iloc[start_idx:end_idx + 1].reset_index(drop=True)

    fig = go.Figure()
    summary_rows = []

    timestamps = pd.to_datetime(df_filtered['Timestamp'])
    time_deltas = timestamps.diff().dt.total_seconds()
    time_deltas = time_deltas.copy()
    time_deltas.iat[0] = 0

    for column in df_filtered.columns[1:]:
        fig.add_trace(go.Scatter(
            x=df_filtered['Timestamp'],
            y=df_filtered[column],
            mode='lines+markers',
            name=column,
            hovertemplate='Time: %{x}<br>Power: %{y:.3f} W'
        ))

        avg_power = df_filtered[column].mean()
        max_power = df_filtered[column].max()
        min_power = df_filtered[column].min()

        energy_joules = (df_filtered[column] * time_deltas).sum()  # watt-seconds (J)
        energy_wh = energy_joules / 3600  # convert to watt-hours (Wh)

        summary_rows.append(html.Tr([
            html.Td(column, style={"border": "1px solid #ccc", "padding": "8px"}),
            html.Td(f"{avg_power:.3f} W", style={"border": "1px solid #ccc", "padding": "8px"}),
            html.Td(f"{max_power:.3f} W", style={"border": "1px solid #ccc", "padding": "8px"}),
            html.Td(f"{min_power:.3f} W", style={"border": "1px solid #ccc", "padding": "8px"}),
            html.Td(f"{energy_wh:.4f} Wh", style={"border": "1px solid #ccc", "padding": "8px"}),
        ]))

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Power (Watts)',
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode='x unified',
        uirevision='constant',
        template='plotly_white',
    )

    summary_table = html.Table([
        html.Thead(html.Tr([
            html.Th("Domain", style={"border": "1px solid #ccc", "padding": "8px", "backgroundColor": "#f2f2f2"}),
            html.Th("Average Power", style={"border": "1px solid #ccc", "padding": "8px", "backgroundColor": "#f2f2f2"}),
            html.Th("Max Power", style={"border": "1px solid #ccc", "padding": "8px", "backgroundColor": "#f2f2f2"}),
            html.Th("Min Power", style={"border": "1px solid #ccc", "padding": "8px", "backgroundColor": "#f2f2f2"}),
            html.Th("Total Energy", style={"border": "1px solid #ccc", "padding": "8px", "backgroundColor": "#f2f2f2"}),
        ])),
        html.Tbody(summary_rows)
    ], style={
        "width": "100%",
        "borderCollapse": "collapse",
        "marginTop": "10px",
        "textAlign": "center"
    })

    return fig, summary_table


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
