from flask.ext.sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

class User (db.Model):
    __tablename__ = "users"
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode)
    email = db.Column('email', db.Unicode)
    username = db.Column('username', db.Unicode)
    password = db.Column('password', db.Unicode)
    register_date = db.Column('register_date', db.Date)
