from AleMoc.database.database import SessionLocal, get_db
from AleMoc.setup import setup_func
from AleMoc.database import models

setup_func()
db = SessionLocal()
api_db = get_db()

ADMIN_USER = db.query(models.SpeschulUsers).filter_by(Login="Admin", Role=models.UserRoles.ADMIN.value).first()

