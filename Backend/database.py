from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ UPDATE 'root' AND 'password' TO YOUR MYSQL CONFIGURATION
# Format: mysql+mysqlconnector://<username>:<password>@<host>/<db_name>
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:admin@localhost/heart_disease_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for API to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
