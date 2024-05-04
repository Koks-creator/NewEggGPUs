from pathlib import Path


class Config:
    PROJECT_MAIN_PATH: str = Path(__file__).resolve().parent
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    UVICORN_LOG_CONFIG_PATH: str = "uvicorn_log_config.json"
    DATABASE_NAME: str = "database"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{PROJECT_MAIN_PATH}/database/{DATABASE_NAME}.db"
    SINK_FOLDER: str = "sink"
    LOGS_FOLDER: str = "logs"
    SCRAPE_ELEMENTS = {
        "Details": {"Tag": "div", "Attr": {"id": "product-details"}},
        "SpecTables": {"Tag": "table", "Attr": {"class": "table-horizontal"}},
        "ProductTitle": {"Tag": "h1", "Attr": {"class": "product-title"}},
        "Price": {"Tag": "li", "Attr": {"class": "price-current"}},
        "Caption": {"Tag": "caption"},
        "Tbody": {"Tag": "tbody"},
        "Trs": {"Tag": "tr"},
        "SpecName": {"Tag": "th"},
        "SpecVal": {"Tag": "td"},
    }
    FIELDS = {
        "Model": ["Brand", "Series", "Model"],
        "Chipset": ["Chipset Manufacturer", "GPU Series", "GPU", "Boost Clock", "CUDA Cores"],
        "Memory": ["Effective Memory Clock", "Memory Size", "Memory Interface", "Memory Type"],
        "Interface": ["Interface"],
        "Ports": ["Multi-Monitor Support", "HDMI", "DisplayPort"]
    }

    REVIEW_FIELDS = {
         "Author": "author",
         "DatePublished": "datePublished",
         "Description": "description",
         "Rating": "reviewRating_ratingValue"
    }
