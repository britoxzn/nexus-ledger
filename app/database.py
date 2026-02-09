from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Por enquanto, usaremos o SQLite (um arquivo local) para facilitar o desenvolvimento.
# Para a produção internacional, trocaremos apenas esta linha por um PostgreSQL.
SQLALCHEMY_DATABASE_URL = "sqlite:///./nexus_ledger_v2.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função que abre e fecha a conexão automaticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()