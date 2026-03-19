from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Database connection URL
# Use 'db' as the host as specified in compose.yaml
DATABASE_URL = "mysql://user:password@db:3306/test_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    company_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

def main():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
