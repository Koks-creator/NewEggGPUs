from datetime import datetime
import plotly.graph_objects as go
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import pandas as pd

from AleMoc.superapp import services


external_css = [dbc.themes.BOOTSTRAP]
app = dash.Dash(
    "Test",
    external_stylesheets=external_css,
)

app.layout = html.Div([
    dcc.Store(id="cache", data=None),
    dcc.Store(id="dataframe", data=None),
    html.H1("xd"),
    dbc.Input(id="phrase_input", value='', type="text"),
    dbc.Button("Search", id="add-phrase-button", n_clicks=0),
    html.H4(id="msg"),
    html.H4(id="msg2"),

    html.Div([
        dcc.Dropdown(id="dropdown-options", multi=True, clearable=True),
    ], style={'maxHeight': '140px', "height": "140px", "overflow-y": "scroll"}),
    dbc.Button("Apply Filter", id="apply-button", n_clicks=0),
    dcc.Graph(id="graph"),
])


@app.callback(Output("msg", "children"),
              [Input("add-phrase-button", "n_clicks")],
              [State("phrase_input", "value")])
def update_message(n_clicks, phrase_input):
    if n_clicks > 0 and phrase_input.strip() != "":
        return f"Phrase: {phrase_input}"
    else:
        return ""


@app.callback([Output('dropdown-options', 'options'),
               Output('dropdown-options', 'value'),
               Output('graph', 'figure')
               ],
              [Input("cache", "data"),
               Input('add-phrase-button', 'n_clicks'),
               Input('apply-button', 'n_clicks'),
               Input('dataframe', 'data'),
               ],
              [State('dropdown-options', 'value')]
              )
def update_options(cache, n_clicks, n_clicks2, dataframe, selected_options):
    if cache:
        options = cache
    else:
        options = []

    if not selected_options:
        selected_options = []
    if "Select All" in selected_options:
        selected_options = options.copy()
        selected_options.remove("Select All")

    fig = {}
    if dataframe:
        df = pd.DataFrame.from_dict(dataframe)

        # filter
        df = df[df["ProductTitle"].isin(selected_options)]
        if len(df):
            x = df["DateCreated"]
            x = pd.to_datetime(x).dt.strftime('%Y-%m-%d %H:%M:%s')
            y = df["Price"]
            labels = df["ProductTitle"]
            urls = df["Url"]

            traces = []
            plot_annotes = []
            for xi, yi, label, url in zip(x, y, labels, urls):
                trace = go.Scatter(
                    x=[xi],
                    y=[yi],
                    mode="markers",
                    marker=dict(size=10, color=services.graph_color_map[label]),
                    name=label[:70],
                    hoverinfo="text",
                    text=f"{yi}$, {label} ({xi.split('.')[0]})",
                )
                traces.append(trace)
                plot_annotes.append(dict(x=xi,
                                         y=yi,
                                         text=f"""<a href="{url}"> </a>""",
                                         showarrow=False,
                                         ))

            layout = go.Layout(
                title="Price History",
                yaxis=dict(title='Price'),
                annotations=plot_annotes
            )

            fig = go.Figure(data=traces, layout=layout)

    return (
        [{'label': option, 'value': option} for option in options],  # Update dropdown options
        selected_options, fig
    )


@app.callback(
    [Output("cache", "data"),
     Output("dataframe", "data")],
    [Input("add-phrase-button", "n_clicks")],
    [State("phrase_input", "value")]
)
def update_cache(n_clicks, phrase):
    # print(c)
    if n_clicks > 0 and phrase.strip() != "":
        df = services.query_table(table_name="Products", where=f"ProductTitle like '%{phrase}%'")
        options = ["Select All"]
        options.extend(df["ProductTitle"].unique().tolist())

        return [options, df.to_dict()]
    return None, None


if __name__ == '__main__':
    app.run_server(debug=True)
