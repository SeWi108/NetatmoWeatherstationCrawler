from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String

Base = declarative_base()


class Measurement(Base):
    __tablename__ = 'measurements'

    time_utc = Column(BigInteger, primary_key=True)
    station_mac = Column(String(17), primary_key=True)
    co2 = Column(Integer)
    noise = Column(Integer)
    temperature = Column(Integer)
