from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from decimal import Decimal
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    balance = db.Column(db.Numeric(10,2), nullable=False, default=Decimal('0.00'))

    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(150), nullable=False)
    recipient = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.sender} -> {self.recipient} : {self.amount}>'

