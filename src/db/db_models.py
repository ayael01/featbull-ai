from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customers'

    name = Column(String, primary_key=True)
    score = Column(Integer, nullable=False)


class Topic(Base):
    __tablename__ = 'topics'

    title = Column(String(255), primary_key=True)


class FeatureRequest(Base):
    __tablename__ = 'feature_requests'

    title = Column(String(255), ForeignKey('topics.title'))
    customer_name = Column(String(255), ForeignKey('customers.name'))
    description = Column(String(1000), primary_key=True)
    time = Column(DateTime, nullable=False)

