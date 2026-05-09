from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Engines for each database
pakka_engine = create_engine(settings.PAKKA_DATABASE_URL, pool_pre_ping=True)
kacha_engine = create_engine(settings.KACHA_DATABASE_URL, pool_pre_ping=True)
shared_engine = create_engine(settings.SHARED_DATABASE_URL, pool_pre_ping=True)

PakkaSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pakka_engine)
KachaSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=kacha_engine)
SharedSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=shared_engine)

Base = declarative_base()
PakkaBase = declarative_base()
KachaBase = declarative_base()


def get_shared_db():
    db = SharedSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pakka_db():
    db = PakkaSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_kacha_db():
    db = KachaSessionLocal()
    try:
        yield db
    finally:
        db.close()
