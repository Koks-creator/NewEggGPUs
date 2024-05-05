from datetime import datetime
from enum import Enum
import sqlalchemy as sql
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash

from AleMoc.database.database import Base


class UserRoles(Enum):
    ADMIN = "Admin"


class Products(Base):
    __tablename__ = "Products"

    Id = sql.Column(sql.Integer, primary_key=True, index=True)
    ProductId = sql.Column(sql.String)
    DateCreated = sql.Column(sql.DateTime, default=datetime.utcnow)
    Archived = sql.Column(sql.BOOLEAN, default=False)
    ProductTitle = sql.Column(sql.String, nullable=True)
    Url = sql.Column(sql.String, nullable=True)
    Price = sql.Column(sql.Float, nullable=True)
    Currency = sql.Column(sql.String)
    Brand = sql.Column(sql.String, nullable=True)
    Series = sql.Column(sql.String, nullable=True)
    Model = sql.Column(sql.String, nullable=True)
    ChipsetManufacturer = sql.Column(sql.String, nullable=True)
    GPUSeries = sql.Column(sql.String, nullable=True)
    GPU = sql.Column(sql.String, nullable=True)
    BoostClock = sql.Column(sql.String, nullable=True)
    CUDACores = sql.Column(sql.String, nullable=True)
    EffectiveMemoryClock = sql.Column(sql.String, nullable=True)
    MemorySize = sql.Column(sql.String, nullable=True)
    MemoryInterface = sql.Column(sql.String, nullable=True)
    MemoryType = sql.Column(sql.String, nullable=True)
    Interface = sql.Column(sql.String, nullable=True)
    MultiMonitorSupport = sql.Column(sql.String, nullable=True)
    HDMI = sql.Column(sql.String, nullable=True)
    DisplayPort = sql.Column(sql.String, nullable=True)

    reviews = orm.relationship("Reviews", back_populates="product")

    def __repr__(self):
        fields = ", ".join([f"{column.name}={getattr(self, column.name)}" for column in self.__table__.columns])
        return f"{self.__class__.__name__}({fields})"


class Reviews(Base):
    __tablename__ = "Reviews"

    Id = sql.Column(sql.Integer, primary_key=True, index=True)
    ProductId = sql.Column(sql.String, sql.ForeignKey("Products.ProductId"))
    ProductTitle = sql.Column(sql.String, nullable=True)
    DateCreated = sql.Column(sql.DateTime, default=datetime.utcnow)
    Author = sql.Column(sql.String)
    DatePublished = sql.Column(sql.DateTime)
    Description = sql.Column(sql.String)
    Rating = sql.Column(sql.Integer)

    # Change the relationship name to 'product' instead of 'products'
    product = orm.relationship("Products", back_populates="reviews")

    def __repr__(self):
        fields = ", ".join([f"{column.name}={getattr(self, column.name)}" for column in self.__table__.columns])
        return f"{self.__class__.__name__}({fields})"


class SpeschulUsers(Base):
    __tablename__ = "SpeschulUsers"

    Id = sql.Column(sql.Integer, primary_key=True, index=True)
    Login = sql.Column(sql.String)
    PasswordHash = sql.Column(sql.String, unique=True)
    Role = sql.Column(sql.String)

    def set_password(self, password: str) -> None:
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.PasswordHash, password)

    def __repr__(self):
        fields = ", ".join([f"{column.name}={getattr(self, column.name)}" for column in self.__table__.columns if column.name != "PasswordHash"])
        return f"{self.__class__.__name__}({fields})"

