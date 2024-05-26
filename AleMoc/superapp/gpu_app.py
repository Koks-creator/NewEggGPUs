from datetime import date
import plotly.graph_objects as go
import dash
from dash import dash_table
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import pandas as pd

from AleMoc.superapp import services, styles


PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"


external_css = [dbc.themes.BOOTSTRAP]
app = dash.Dash(
    "GpuApp",
    external_stylesheets=external_css,
)


navbar = dbc.Navbar(
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
            dbc.Col(dbc.NavbarBrand("I dunno...", className="ms-2")),
        ]), color="dark", dark=True
    , style={"padding": "20px"}
)

footer = dbc.Navbar(
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
            dbc.Col(dbc.NavbarBrand("Don't judge my styling", className="ms-2")),
        ]), color="dark", dark=True
    , style={"padding": "20px", "marginTop": "80px"}
)

app.layout = html.Div([
    navbar,
    dcc.Store(id="cache", data=None),
    dcc.Store(id="products-dataframe", data=None),
    dcc.Store(id="reviews-dataframe", data=None),
    html.H1("Turbo GPU App", style={"textAlign": "center", "marginTop": "30px", "marginBottom": "30px"}),
    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                dbc.InputGroup([
                        dbc.Input(id="phrase_input", value='', type="text", style={"background-color": "rgb(232, 240, 254)"}),
                        dcc.DatePickerRange(
                                id='date-picker',
                                min_date_allowed=date(1900, 1, 1),
                                max_date_allowed=date(9999, 1, 1),
                                initial_visible_month=date(2024, 5, 1),

                            ),
                        dbc.Button("Search", id="add-phrase-button", n_clicks=0),
                ]),
                dbc.Spinner(html.H4(id="phrase"))

            ]), style={"width": "95%", "background-color": "#f0ebd8"}
        ),
        ], align="center", justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H5("Select something and apply"),
                    dcc.Dropdown(id="dropdown-options", multi=True, clearable=True, style={"background-color": "rgb(232, 240, 254)"}),
                ], style={'maxHeight': '140px', "height": "120px", "overflow-y": "scroll"}),
                dbc.Button("Apply Filter", id="apply-button", n_clicks=0, style={"marginTop": "10px"})
            ]), style={"width": "95%", "background-color": "#f0ebd8"}
        ),
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id="graph")
            ]), style={"width": "95%", "marginTop": "28px", "background-color": "#f0ebd8"}
        ),
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.Div(id="table"), width=9),
                    dbc.Col(
                        dcc.Graph(id="ratings-pie-chart")
                        , width=3
                    )
                ])
            ]), style={"width": "95%", "marginTop": "28px", "background-color": "#f0ebd8"}
        )
        ], align="center", justify="center"),
    footer
], style={"background-color": "#748cab"})


@app.callback([Output('dropdown-options', 'options'),
               Output('dropdown-options', 'value'),
               Output('graph', 'figure'),
               Output('table', 'children'),
               Output('ratings-pie-chart', 'figure'),
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

    pie_fig = go.Figure()
    chart_fig = go.Figure()
    table = dash_table.DataTable()
    if dataframe_products and reviews_dataframe:
        df_products = pd.DataFrame.from_dict(dataframe_products)
        df_products = df_products[df_products["Price"].notna()]

        if len(df_products):
            df_products['DateCreated'] = pd.to_datetime(df_products['DateCreated'])
            df_products["DateCreated"] = df_products["DateCreated"].dt.strftime('%Y-%m-%d %H:%M:%')
            df_products = df_products[df_products["ProductTitle"].isin(selected_options)]

            # Reviews #
            df_reviews = pd.DataFrame.from_dict(reviews_dataframe)
            df_reviews = df_reviews[df_reviews["ProductTitle"].isin(selected_options)]
            df_reviews["DatePublished"] = pd.to_datetime(df_reviews["DatePublished"]).dt.strftime("%Y-%m-%d")

            # join
            df_table = df_reviews.merge(df_products, on="ProductId")

            # Create column with link
            df_table["Product"] = [f"""[{row[1]["ProductTitle_x"]}]({row[1]["Url"]})""" for row in
                                   df_table[["ProductTitle_x", "Url"]].iterrows()]
            df_table = df_table[["Product", "Description", "Rating", "DatePublished", "Author"]]

            # Ratings #
            df_ratings = df_reviews.groupby("Rating").count()

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
                annotations=plot_annotes,
            )

            chart_fig = go.Figure(data=traces, layout=layout)

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
                style_data_conditional=styles.style_data_conditional,
                style_data=styles.style_data
            )

            pie_labels = [f"Rating: {rate}" for rate in df_ratings.index.tolist()]
            pie_fig = go.Figure(
                data=[
                    go.Pie(labels=pie_labels, values=df_ratings["Id"].tolist())
                ]
            )
            pie_fig.update_layout(title_text="Ratings Percentage")

    chart_fig.update_layout(
        paper_bgcolor='#c5baaf',
        plot_bgcolor='lightgrey'
    )
    pie_fig.update_layout(
        paper_bgcolor='#c5baaf',
        plot_bgcolor='lightgrey'
    )
    return (
        [{'label': option, 'value': option} for option in options],  # Update dropdown options
        selected_options, chart_fig, table, pie_fig
    )


@app.callback(
    [Output("cache", "data"),
     Output("products-dataframe", "data"),
     Output("reviews-dataframe", "data"),
     Output("phrase", "children")
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

        return [options, df_products.to_dict(), df_reviews.to_dict(), f"Phrase: {phrase}"]
    return None, None, None, "Provide phrase, 'rtx 3080' for example"


if __name__ == '__main__':
    app.run_server(debug=True)
