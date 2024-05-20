# table
style_table = {
    'height': '627px',
    'overflowY': 'auto',
}

style_cell = {
    "whiteSpace": "normal",
    "overflow": "hidden",
    "textOverflow": "ellipsis",
    }

style_header = {
    "textAlign": "left"
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
        "backgroundColor": "#386641"

    },
    {
        "if": {
            "filter_query": "{Rating} <= 2",
            "column_id": ["Rating"]
        },
        "backgroundColor": "#ae2012"

    },
    {
        "if": {
            "filter_query": "{Rating} > 2 && {Rating} < 4",
            "column_id": ["Rating"]
        },
        "backgroundColor": "#fcbf49"

    }

]

