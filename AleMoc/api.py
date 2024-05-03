from typing import Annotated, List, Union, Optional
import logging
from functools import wraps
from random import randint
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from sqlalchemy.orm import Session
from sqlalchemy.exc import InvalidRequestError, OperationalError


from AleMoc import get_db, ADMIN_USER
from AleMoc.database import models, db_services
from AleMoc import schemas
from AleMoc.scraper import scraper


app = FastAPI()
security = HTTPBasic()
sc = scraper.NewEggScraper(log_level=logging.INFO)


def requires_authentication(func):  # func refers to 'decorated' function, so in this case to route function
    @wraps(func)
    def wrapper(*args, **kwargs):
        credentials = kwargs.get("credentials")
        if not authentication_check(credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return func(*args, **kwargs)
    return wrapper


def authentication_check(credentials: HTTPBasicCredentials) -> bool:
    current_username_bytes = credentials.username.encode("utf8")

    correct_username_bytes = ADMIN_USER.Login.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    is_correct_password = ADMIN_USER.check_password(credentials.password)

    return all([is_correct_username, is_correct_password])


@app.get("/status")
@app.get("/")
def api_status():
    return "Hello, i'm alive"


@app.post("/queryTable/", response_model=List[Union[schemas.ProductSchema, schemas.ReviewSchema]])
def query_table(query: schemas.QueryTable,
                db: Session = Depends(get_db),
                ):
    try:
        res = db_services.query_table(db=db, table_name=query.table_name, query_filter=query.query_filter)
        return res
    except KeyError as ke_exc:
        raise HTTPException(status_code=500, detail=f"No such table {ke_exc}")
    except InvalidRequestError as ire_exc:
        raise HTTPException(status_code=500,
                            detail=str(ire_exc))


@app.post("/queryTableSql/", response_model=schemas.QueryTableSqlResp)
def query_table_sql(query: schemas.QueryTableSql,
                    db: Session = Depends(get_db),
                    ):

    try:
        res = db_services.query_table_sql(db=db, table_name=query.table_name, query_filter=query.query_filter)
        columns = db_services.TABLES[query.table_name]["Columns"]
        if query.query_filter["Columns"]:
            columns = query.query_filter["Columns"]

        # you can use zip to create column: value list of dicts in query_table_sql but it takes too much time
        return {"Columns": columns, "Result": res}
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except db_services.SqlInjectionException:
        return "Your where clause contained one of these: update, delete," \
               " insert, drop, alter, truncate. Fuck you."


# Needs Auth
@app.put("/updateTable", response_model=List[Union[schemas.ProductSchema, schemas.ReviewSchema]])
@requires_authentication
def update_table(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                 update_query: schemas.UpdateTable,
                 db: Session = Depends(get_db)):
    try:
        res = db_services.update_table(db=db, table_name=update_query.table_name,
                                       query_filter=update_query.query_filter,
                                       updated_fields=update_query.updated_fields,
                                       rollback=update_query.rollback)
        return res
    except KeyError as ke_exc:
        raise HTTPException(status_code=500, detail=f"No such table {ke_exc}")
    except InvalidRequestError as ire_exc:
        raise HTTPException(status_code=500, detail=str(ire_exc))


@app.put("/updateTableSql")
@requires_authentication
def update_table_sql(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                     update_query: schemas.UpdateTableSql,
                     db: Session = Depends(get_db)):

    try:
        res = db_services.update_table_sql(db=db, table_name=update_query.table_name,
                                           update_query=update_query.update_query,
                                           rollback=update_query.rollback)
        return {"UpdatedRecordsCount": res}
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except db_services.SqlInjectionException:
        return "Your where or set clause contained one of these: update, delete," \
               " insert, drop, alter, truncate. Fuck you."


@app.delete("/deleteFromTable")
@requires_authentication
def delete_from_table(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                      delete_query: schemas.DeleteFromTable,
                      db: Session = Depends(get_db)):
    try:
        res = db_services.delete_from_table(db=db, table_name=delete_query.table_name,
                                            query_filter=delete_query.query_filter,
                                            rollback=delete_query.rollback)
        return {"DeletedRecordsCount": res}
    except KeyError as ke_exc:
        raise HTTPException(status_code=500, detail=f"No such table {ke_exc}")
    except InvalidRequestError as ire_exc:
        raise HTTPException(status_code=500, detail=str(ire_exc))


@app.delete("/deleteFromTableSql")
@requires_authentication
def delete_from_table_sql(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                          delete_query: schemas.DeleteFromTableSql,
                          db: Session = Depends(get_db)):
    try:
        res = db_services.delete_from_table_sql(db=db, table_name=delete_query.table_name,
                                                query_filter=delete_query.query_filter,
                                                rollback=delete_query.rollback)
        return {"DeletedRecordsCount": res}
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except db_services.SqlInjectionException:
        return "Your where clause contained one of these: update, delete," \
               " insert, drop, alter, truncate. Fuck you."


@app.post("/runScraper")
@requires_authentication
def run_scraper(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                scraper_config: schemas.ScraperSchema,
                db: Session = Depends(get_db)):

    execution_id = f"{randint(1, 1000000):06d}"
    try:
        prods, reviews, folder = sc.start_scraping(phrase=scraper_config.phrase.strip().replace(" ", "+"),
                                                   max_pages=scraper_config.limit,
                                                   execution_id=execution_id)
        folder = folder.split("/")[-1]
        if scraper_config.add_to_db:
            db_services.add_data_from_sink(db=db, folders_to_process=[folder])
            return {"Msg": "added", "Products": prods, "Reviews": reviews}, status.HTTP_201_CREATED
        else:
            return {"Msg": "done", "Products": prods, "Reviews": reviews}
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"Error occurred: {e}"
        )


@app.get("/listSink")
@requires_authentication
def list_sink(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"SinkFiles": db_services.list_sink()}


@app.post("/processSink", status_code=201)
@requires_authentication
def process_sink(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                 sink_process: schemas.SinkProcessSchema, db: Session = Depends(get_db)):

    sink_folders = db_services.list_sink()
    non_exist = [f for f in sink_process.folder_names if f not in sink_folders]

    if not sink_folders:
        raise HTTPException(
            status_code=404,
            detail=f"Sink folder is empty"
        )
    if non_exist:
        raise HTTPException(
            status_code=500,
            detail=f"These folders doesn't exist: {non_exist}"
        )
    return db_services.add_data_from_sink(db=db, folders_to_process=sink_process.folder_names)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
