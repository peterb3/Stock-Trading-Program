from flask import Flask, render_template, request, flash, redirect, url_for
from config import Config
from models import db, Stock, Balance
from stock_service import StockService

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def index():
    stock = Stock.query.first()
    balance = Balance.query.first()
    return render_template('index.html', stock=stock, balance=balance)

@app.route("/trade", methods = ['GET', 'POST'])
def trade():
    stock = Stock.query.first()
    balance = Balance.query.first()
    if request.method == 'POST' and request.form.get('action') == 'search':
        symbol = request.form.get('symbol').upper()
        return redirect(url_for('stock_details', symbol=symbol))
    return render_template('trade.html', stock=stock, balance=balance)

@app.route("/search", methods=['POST'])
def search():
    symbol = request.form.get('symbol').upper()
    return redirect(url_for('stock_details', symbol=symbol))

@app.route("/stock/<symbol>")
def stock_details(symbol):
    price = StockService.get_stock_price(symbol)
    if price is None:
        flash(f'Failed to fetch price for stock {symbol}. Please try again.', 'danger')
        return redirect(url_for('trade'))
    return render_template('stock_details.html', symbol=symbol, price=price)

@app.route("/buy", methods=['POST'])
def buy():
    symbol = request.form.get('symbol')
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        stock = Stock(symbol=symbol, quantity=0, purchase_price=0)
    quantity = int(request.form.get('quantity'))
    stock.purchase_price = StockService.get_stock_price(symbol)
    balance = Balance.query.first()
    total_cost = quantity * stock.purchase_price
    if total_cost <= balance.amount:
        stock.quantity += quantity
        balance.amount -= total_cost
        db.session.add(stock)
        db.session.commit()
        flash(f'Bought {quantity} shares of {stock.symbol}!', 'success')
    else:
        flash('Not enough money to buy!', 'danger')
    return redirect(url_for('trade'))

@app.route("/sell", methods=['POST'])
def sell():
    symbol = request.form.get('symbol')
    stock = Stock.query.filter_by(symbol=symbol).first()
    if stock:
        balance = Balance.query.first()
        quantity = int(request.form.get('quantity'))
        if stock.quantity >= quantity:
            curr_price = StockService.get_stock_price(symbol)
            stock.purchase_price = curr_price
            stock.quantity -= quantity
            balance.amount += quantity * stock.purchase_price
            db.session.commit()
            flash(f'Sold {quantity} shares of {stock.symbol}!', 'success')
        else:
            flash('Not enough shares to sell!', 'danger')
    else:
        flash(f'Stock {symbol} not found in portfolio!', 'danger')
    return redirect(url_for('trade'))

if __name__ == "__main__":
    with app.app_context():
        db.drop_all() #drop tables at beginning for development, remove for persistence
        db.create_all()
        if not Stock.query.first():
            stock = Stock(symbol="AAPL", purchase_price=StockService.get_stock_price('AAPL'), quantity=1)
            db.session.add(stock)
            db.session.add(Balance(amount=10000.00))
            db.session.commit()
    app.run(debug=True)
