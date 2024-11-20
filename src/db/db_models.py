from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customers'

    name = Column(String, primary_key=True)
    score = Column(Integer, nullable=False)
