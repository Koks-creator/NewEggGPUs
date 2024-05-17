import plotly.graph_objects as go
import dash
from dash import dash_table
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
    dcc.Store(id="products-dataframe", data=None),
    dcc.Store(id="reviews-dataframe", data=None),
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
html.Div(id="table")
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
               Input('products-dataframe', 'data'),
               Input("reviews-dataframe", "data")
               ],
              [State('dropdown-options', 'value')]
              )
def update_options(cache, n_clicks, n_clicks2, dataframe_products, reviews_dataframe, selected_options):

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
    if dataframe_products and reviews_dataframe:
        df_products = pd.DataFrame.from_dict(dataframe_products)
        df_products = df_products[df_products["Price"].notna()]

        df_reviews = pd.DataFrame.from_dict(reviews_dataframe)

        # filter
        df_products = df_products[df_products["ProductTitle"].isin(selected_options)]
        if len(df_products):
            # x = df["DateCreated"]
            # x = pd.to_datetime(x).dt.strftime('%Y-%m-%d %H:%M:%s')
            # y = df["Price"]
            # labels = df["ProductTitle"]
            # urls = df["Url"]
            # spechs = df[["Brand", "Series", "Model", "ChipsetManufacturer", "GPUSeries", "GPU"]]
            df_products['DateCreated'] = pd.to_datetime(df_products['DateCreated'])
            df_products["DateCreated"] = df_products["DateCreated"].dt.strftime('%Y-%m-%d %H:%M:%')
            traces = []
            plot_annotes = []
            # for xi, yi, label, url in zip(x, y, labels, urls):
            rows = df_products.iterrows()
            for ind, row in rows:
                trace = go.Scatter(
                    x=[row["DateCreated"]],
                    y=[row["Price"]],
                    mode="markers",
                    marker=dict(size=10, color=services.graph_color_map[row["ProductTitle"]]),
                    name=row["ProductTitle"][:70],
                    hoverinfo="text",
                    text=services.create_tooltip(row=row),
                )
                traces.append(trace)
                plot_annotes.append(dict(x=row["DateCreated"],
                                         y=row["Price"],
                                         text=f"""<a href="{row["Url"]}"> </a>""",
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
     Output("products-dataframe", "data"),
     Output("reviews-dataframe", "data")
     ],
    [Input("add-phrase-button", "n_clicks")],
    [State("phrase_input", "value")]
)
def update_cache(n_clicks, phrase):
    if n_clicks > 0 and phrase.strip() != "":
        df_products = services.query_table(table_name="Products", where=f"ProductTitle like '%{phrase}%'")
        df_reviews = services.query_table(table_name="Reviews", where=f"ProductTitle like '%{phrase}%'")
        options = ["Select All"]
        options.extend(df_products["ProductTitle"].unique().tolist())

        return [options, df_products.to_dict(), df_reviews.to_dict()]
    return None, None, None


if __name__ == '__main__':
    app.run_server(debug=True)
