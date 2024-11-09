from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Defining Stock database entry; contains a symbol, quantity, and purchase price
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)

# Defining user money entry; contains the free cash amount
class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
