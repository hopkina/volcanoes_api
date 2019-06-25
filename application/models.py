from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from application import app

# connect to the database
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# define the Volcano class, which will model the Volcano database table
class Volcano(Base):
    __tablename__ = 'volcano'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    elevation = Column(Float)
    volcano_type = Column(String)
    longitude = Column(Float)
    latitude = Column(Float)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    continent_id = Column(Integer, ForeignKey('continent.id'))
    continent_ref = relationship("Continent", backref='country')
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))


class Continent(Base):
    __tablename__ = 'continent'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    countries = relationship('Country', backref='continent')
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
