from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.Integer, primary_key=True)
    userEmail = db.Column(db.String, nullable=False)
    userPassword = db.Column(db.String, nullable=False)

class Tutor(db.Model):
    __tablename__ = 'tutor'
    tutorID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)

class Request(db.Model):
    __tablename__ = 'request'
    requestID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    tutorID = db.Column(db.Integer, db.ForeignKey('tutor.tutorID'), nullable=True)
    unit = db.Column(db.String, nullable=False)
