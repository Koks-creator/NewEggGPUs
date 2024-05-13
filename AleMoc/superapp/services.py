import requests
import pandas as pd
import numpy as np

BASE_URL = "http://127.0.0.1:8000/"  # ProductTitle like 'RTX%3070%'


def query_table(table_name: str, where: str, columns: list = None) -> pd.DataFrame:
    if not columns:
        columns = []
    resp = requests.post(f"{BASE_URL}queryTableSql", json={
        "table_name": table_name,
        "query_filter": {
            "WhereQuery": where,
            "Columns": columns}
        }
        )

    res = resp.json()

    df = pd.DataFrame(data=res["Result"], columns=res["Columns"])
    return df


graph_color_map = {label: np.random.rand(3, ) for label in query_table(table_name="Products", where="")["ProductTitle"]}

if __name__ == '__main__':
    df = query_table(table_name="Products", where="")
    xd = pd.to_datetime(df["DateCreated"])
    x = xd.dt.strftime('%Y-%m-%d %H:%M:%S')

    print(x)
