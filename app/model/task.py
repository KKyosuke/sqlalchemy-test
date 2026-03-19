from sqlalchemy import Column, Integer, String, TIMESTAMP
import datetime
from app.database import Base
from app.model.mixin import CompanyMixin

class Task(Base, CompanyMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    todo = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
