from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, func


engine = create_engine("postgresql://app:1234@127.0.0.1:5431/app")
Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)

class Advertisement(Base):

    __tablename__ = "app_advertisement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    owner = Column(String, nullable=False)
    creation_date = Column(DateTime, server_default=func.now())

Base.metadata.create_all()
