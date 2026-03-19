from sqlalchemy import Column, Integer, String, TIMESTAMP
import datetime
from app.database import Base
from app.model.mixin import CompanyMixin

class User(Base, CompanyMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
