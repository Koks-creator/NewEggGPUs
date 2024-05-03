from datetime import datetime
from typing import Union, List
from typing_extensions import TypedDict
import pydantic

from AleMoc.database import models


class BaseModel(pydantic.BaseModel):
    table_name: str


# DB objects
class ProductSchema(pydantic.BaseModel):
    Id: int
    ProductId: str
    DateCreated: datetime
    Archived: bool
    ProductTitle: Union[str, None]
    Url: Union[str, None]
    Price: Union[float, None]
    Currency: Union[str, None]
    Brand: Union[str, None]
    Series: Union[str, None]
    Model: Union[str, None]
    ChipsetManufacturer: Union[str, None]
    GPUSeries: Union[str, None]
    GPU: Union[str, None]
    BoostClock: Union[str, None]
    CUDACores: Union[str, None]
    EffectiveMemoryClock: Union[str, None]
    MemorySize: Union[str, None]
    MemoryInterface: Union[str, None]
    MemoryType: Union[str, None]
    Interface: Union[str, None]
    MultiMonitorSupport: Union[str, None]
    HDMI: Union[str, None]
    DisplayPort: Union[str, None]


class ReviewSchema(pydantic.BaseModel):
    Id: int
    ProductId: str
    DateCreated: datetime
    Author: str
    DatePublished: datetime
    Description: str
    Rating: int


# scraper
class ScraperSchema(pydantic.BaseModel):
    phrase: str
    limit: int = 0
    add_to_db: bool = True


class SinkProcessSchema(pydantic.BaseModel):
    folder_names: list


# TypedDicts
class SelectQueryFilter(TypedDict):
    WhereQuery: str
    Columns: List[str]


class UpdateQuery(TypedDict):
    WhereQuery: str
    SetQuery: str


class DeleteQuery(TypedDict):
    WhereQuery: str


# Inputs

class QueryTable(BaseModel):
    query_filter: dict


class QueryTableSql(BaseModel):
    query_filter: SelectQueryFilter


class UpdateTable(BaseModel):
    query_filter: dict
    updated_fields: dict
    rollback: bool = True


class UpdateTableSql(BaseModel):
    update_query: UpdateQuery
    rollback: bool


class DeleteFromTable(BaseModel):
    query_filter: dict
    rollback: bool = True


class DeleteFromTableSql(BaseModel):
    query_filter: DeleteQuery
    rollback: bool = True


# Response models
class QueryTableSqlResp(pydantic.BaseModel):
    Columns: List[str]
    Result: List[List]
