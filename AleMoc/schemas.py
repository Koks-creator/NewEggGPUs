from datetime import datetime
from typing import Union, List
from typing_extensions import TypedDict
import pydantic

from AleMoc.database import models

'''
zrob schema dla review i product
'''


class ProductSchema(pydantic.BaseModel):
    Id: int
    ProductId: str
    DateCreated: datetime
    Archived: bool
    ProductTitle: str
    Url: str
    Price: float
    Currency: str
    Brand: str
    Series: str
    Model: str
    ChipsetManufacturer: str
    GPUSeries: str
    GPU: str
    BoostClock: str
    CUDACores: str
    EffectiveMemoryClock: str
    MemorySize: str
    MemoryInterface: str
    MemoryType: str
    Interface: str
    MultiMonitorSupport: str
    HDMI: str
    DisplayPort: str


class ReviewSchema(pydantic.BaseModel):
    Id: int
    ProductId: str
    DateCreated: datetime
    Author: str
    DatePublished: datetime
    Description: str
    Rating: int


class ScraperSchema(pydantic.BaseModel):
    phrase: str
    limit: int = 0
    add_to_db: bool = True


class BaseModel(pydantic.BaseModel):
    table_name: str


class QueryTable(BaseModel):
    query_filter: dict


class xdtest(TypedDict):
    WhereQuery: List[str]
    Columns: List[str]


class QueryTableSql(BaseModel):
    query_filter: xdtest
