from typing import Annotated
import logging
from random import randint
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from sqlalchemy.orm import Session
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from AleMoc import get_db, ADMIN_USER
from AleMoc.database import models, db_services
from AleMoc import schemas
from AleMoc.scraper import scraper


app = FastAPI()
security = HTTPBasic()
sc = scraper.NewEggScraper(log_level=logging.INFO)


def authentication_check(credentials: HTTPBasicCredentials) -> bool:
    current_username_bytes = credentials.username.encode("utf8")

    correct_username_bytes = ADMIN_USER.Login.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    is_correct_password = ADMIN_USER.check_password(credentials.password)

    return all([is_correct_username, is_correct_password])


@app.get("/status")
def api_status():
    return "Hello, i'm alive"


@app.post("/runScraper")
def run_scraper(scraper_config: schemas.ScraperSchema):
    execution_id = f"{randint(1, 1000000):06d}"

    try:
        sc.start_scraping(phrase=scraper_config.phrase, max_pages=scraper_config.limit, execution_id=execution_id)
        if scraper_config.add_to_db:
            return {"Msg": "added"}, status.HTTP_201_CREATED
        else:
            return {"Msg": "done"}
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"Error occured: {e}"
        )


@app.post("/queryTable/")
def query_table(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                query: schemas.QueryTable,
                db: Session = Depends(get_db),
                ):
    if not authentication_check(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    res = db_services.query_table(db=db, table_name=query.table_name, query_filter=query.query_filter)
    return res


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)