from datetime import date
import plotly.graph_objects as go
import dash
from dash import dash_table
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import pandas as pd

from AleMoc.superapp import services, styles


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
    dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date(9999, 1, 1),
            initial_visible_month=date(2024, 5, 1),
            # end_date=date(9999, 1, 1),
            # start_date=date(1900, 1, 1)
        ),
    dbc.Button("Search", id="add-phrase-button", n_clicks=0),
    html.H4(id="msg"),
    html.H4(id="msg2"),

    html.Div([
        dcc.Dropdown(id="dropdown-options", multi=True, clearable=True),
    ], style={'maxHeight': '140px', "height": "140px", "overflow-y": "scroll"}),
    dbc.Button("Apply Filter", id="apply-button", n_clicks=0),
    dcc.Graph(id="graph"),
    html.Div(id="table", style={"width": "1400px"})
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
               Output('graph', 'figure'),
               Output('table', 'children')
               ],
              [Input("cache", "data"),
               Input('add-phrase-button', 'n_clicks'),
               Input('apply-button', 'n_clicks'),
               Input('products-dataframe', 'data'),
               Input("reviews-dataframe", "data"),
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
    table = dash_table.DataTable()
    if dataframe_products and reviews_dataframe:
        df_products = pd.DataFrame.from_dict(dataframe_products)
        df_products = df_products[df_products["Price"].notna()]

        df_reviews = pd.DataFrame.from_dict(reviews_dataframe)

        # filter
        df_products = df_products[df_products["ProductTitle"].isin(selected_options)]
        df_reviews = df_reviews[df_reviews["ProductTitle"].isin(selected_options)]
        df_reviews["DatePublished"] = pd.to_datetime(df_reviews["DatePublished"]).dt.strftime("%Y-%m-%d")
        # join
        df_table = pd.concat([df_reviews, df_products], axis=1, join='inner')
        df_table = df_table.loc[:, ~df_table.columns.duplicated()].copy()
        #  https://stackoverflow.com/questions/14984119/python-pandas-remove-duplicate-columns
        df_table["Product"] = [f"""[{row[1]["ProductTitle"]}]({row[1]["Url"]})""" for row in
                           df_table[["ProductTitle", "Url"]].iterrows()]
        df_table = df_table[["Product", "Description", "Rating", "DatePublished", "Author"]]

        if len(df_products):
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

            table = dash_table.DataTable(
                data=df_table.to_dict("records"),
                columns=[{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'Product' else {'id': x, 'name': x}
                         for x in df_table.columns],
                style_table=styles.style_table,
                style_as_list_view=True,
                page_action='native',
                page_current=0,
                page_size=10,
                style_cell=styles.style_cell,
                style_header=styles.style_header,
                style_cell_conditional=styles.style_cell_conditional,
                style_data_conditional=styles.style_data_conditional
            )

    return (
        [{'label': option, 'value': option} for option in options],  # Update dropdown options
        selected_options, fig, table
    )


@app.callback(
    [Output("cache", "data"),
     Output("products-dataframe", "data"),
     Output("reviews-dataframe", "data")
     ],
    [Input("add-phrase-button", "n_clicks"),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')
     ],
    [State("phrase_input", "value")]
)
def update_cache(n_clicks, start_date, end_date, phrase):
    if n_clicks > 0 and phrase.strip() != "":
        start_date = start_date if start_date else "2000-01-01"
        end_date = end_date if end_date else "2100-01-01"
        where_clause = f"ProductTitle LIKE '%{phrase}%' AND DateCreated BETWEEN '{start_date}' AND '{end_date}'"

        df_products = services.query_table(table_name="Products", where=where_clause)
        df_reviews = services.query_table(table_name="Reviews", where=where_clause)

        options = ["Select All"]
        options.extend(df_products["ProductTitle"].unique().tolist())

        return [options, df_products.to_dict(), df_reviews.to_dict()]
    return None, None, None


if __name__ == '__main__':
    app.run_server(debug=True)
