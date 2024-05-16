from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker



Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    userID = Column(Integer, primary_key=True)
    userEmail = Column(String, unique=True, nullable=False)
    userPassword = Column(String, nullable=False)
    requests = relationship('Request', back_populates='user')

class Tutor(Base):
    __tablename__ = 'tutor'
    tutorID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('user.userID'), nullable=False)
    requests = relationship('Request', back_populates='tutor')

class Request(Base):
    __tablename__ = 'request'
    requestID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('user.userID'), nullable=False)
    tutorID = Column(Integer, ForeignKey('tutor.tutorID'), nullable=True)
    unit = Column(String, nullable=False)
    user = relationship('User', back_populates='requests')
    tutor = relationship('Tutor', back_populates='requests')


engine = create_engine('sqlite:///site.db', echo=True)
Base.metadata.create_all(engine)