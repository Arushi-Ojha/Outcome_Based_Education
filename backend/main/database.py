import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

# Create connection URL using PyMySQL
# TiDB is compatible with MySQL protocols
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Create engine
# We use pymysql as it is a pure Python MySQL client, well supported with TiDB.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "ssl_verify_cert": True,
        "ssl_verify_identity": True
    },
    echo=False,  # Set to True to see SQL queries in development
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
