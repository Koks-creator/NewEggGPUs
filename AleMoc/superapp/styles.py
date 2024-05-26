# table
style_table = {
    "height": "627px",
    "overflowY": "auto",
    "border": "1px solid #ced4da"
}
style_data = {
    "backgroundColor": "lightblue",
    "color": "black"
}

style_cell = {
    "whiteSpace": "normal",
    "overflow": "hidden",
    "textOverflow": "ellipsis",
    }

style_header = {
    "textAlign": "left",
    "backgroundColor": "#c5baaf",
    "color": "black",
    "fontWeight": "bold"
}

style_cell_conditional = [
    {
        "if": {
            "column_id": "ProductTitle",
        },
        "width": "20%", "whiteSpace": "normal", "textAlign": "left"
    },
    {
        "if": {
            "column_id": "Description"
        },
        "width": "65%", "whiteSpace": "normal", "textAlign": "left"
    },
    {
        "if": {
            "column_id": "Rating"
        },
        "width": "5%", "whiteSpace": "normal", "textAlign": "center"
    },
    {
        "if": {
            "column_id": "Author"
        },
        "width": "10%", "whiteSpace": "normal", "textAlign": "center"
    }
]


style_data_conditional = [
    {
        "if": {
            "filter_query": "{Rating} >= 4",
            "column_id": ["Rating"]
        },
        "backgroundColor": "#16db65"

    },
    {
        "if": {
            "filter_query": "{Rating} <= 2",
            "column_id": ["Rating"]
        },
        "backgroundColor": "#e63946"

    },
    {
        "if": {
            "filter_query": "{Rating} > 2 && {Rating} < 4",
            "column_id": ["Rating"]
        },
        "backgroundColor": "#fcbf49"

    }

]

