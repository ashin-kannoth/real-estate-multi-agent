from sqlalchemy import create_engine, Column, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid

Base = declarative_base()

class CustomerDB(Base):
    __tablename__ = "customers"
    id       = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name     = Column(String)
    email    = Column(String)
    phone    = Column(String)
    budget   = Column(Float)
    location = Column(String)

class PropertyDB(Base):
    __tablename__ = "properties"
    id       = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title    = Column(String)
    location = Column(String)
    price    = Column(Float)
    details  = Column(JSON)

engine  = create_engine(
    "sqlite:///./realestate.db",
    connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)