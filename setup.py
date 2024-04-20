from AleMoc.database.database import create_database, SessionLocal
from AleMoc.database import models


def setup_func():
    print("d")
    create_database()

    db = SessionLocal()
    if not db.query(models.SpeschulUsers).all():
        speschul_user = models.SpeschulUsers(
            Login="Admin",
            Role=models.UserRoles.ADMIN.value
        )
        speschul_user.set_password("admin")  # you probably would like to store password as env variable (at least)
                                             # or in key vault - I just didn't care
        db.add(speschul_user)
        db.commit()
        db.refresh(speschul_user)


if __name__ == '__main__':
    setup_func()
