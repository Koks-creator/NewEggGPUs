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


def create_tooltip(row: pd.Series):
    return f'{row["ProductTitle"]} <br>' \
           f'DateCreated: {row["DateCreated"][:-4]}<br>' \
           f'Price: {row["Price"]}$<br>' \
           f'ProductId: {row["ProductId"]}<br>' \
           f'Brand: {row["Brand"]}<br>' \
           f'Series: {row["Series"]}<br>' \
           f'Model: {row["Model"]}<br>' \
           f'ChipsetManufacturer: {row["ChipsetManufacturer"]}<br>' \
           f'GPUSeries: {row["GPUSeries"]}<br>' \
           f'GPU: {row["GPU"]}<br>' \
           f'BoostClock: {row["BoostClock"]}<br>' \
           f'CUDACores: {row["CUDACores"]}<br>' \
           f'EffectiveMemoryClock: {row["EffectiveMemoryClock"]}<br>' \
           f'MemorySize: {row["MemorySize"]}<br>' \
           f'MemoryInterface: {row["MemoryInterface"]}<br>' \
           f'MemoryType: {row["MemoryType"]}<br>' \
           f'Interface: {row["Interface"]}<br>' \
           f'MemorySize: {row["MemorySize"]}<br>' \
           f'MultiMonitorSupport: {row["MultiMonitorSupport"]}<br>' \
           f'HDMI: {row["HDMI"]}<br>' \
           f'DisplayPort: {row["DisplayPort"]}<br>' \



graph_color_map = {label: np.random.rand(3, ) for label in query_table(table_name="Products", where="")["ProductTitle"]}

if __name__ == '__main__':
    #ProductTitle LIKE '%rtx 3070%' AND DateCreated BETWEEN '2024-05-01' AND '2024-05-31'
    phrase = "%rtx 3070%"
    start_date = "2024-05-01"
    end_date = "2024-05-31"
    df = query_table(table_name="Reviews", where="")
    df = df.groupby("Rating").count()
    print(df["Id"].head())
    print(df.index)
    # df = query_table(table_name="Products", where="")
    # # spechs = df[["Brand", "Series", "Model", "ChipsetManufacturer", "GPUSeries", "GPU"]]
    # rows = df.iterrows()
    # for ind, row in rows:
    #     print(create_tooltip(row))
    #     break

