import logging
import json
from fastapi import FastAPI
from fastapi.security import HTTPBasic

from AleMoc.database.database import SessionLocal, get_db
from AleMoc.setup import setup_func
from AleMoc.database import models
from AleMoc.scraper import scraper
from AleMoc.config import Config

setup_func()
db = SessionLocal()

ADMIN_USER: models.SpeschulUsers = db.query(models.SpeschulUsers).filter_by(
    Login="Admin",
    Role=models.UserRoles.ADMIN.value
).first()

with open(f"{Config.PROJECT_MAIN_PATH}/{Config.UVICORN_LOG_CONFIG_PATH}") as f:
    uvicorn_log_config = json.load(f)

app = FastAPI()
security = HTTPBasic()
sc = scraper.NewEggScraper(log_level=logging.INFO)

from AleMoc import routes
