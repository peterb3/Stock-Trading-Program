from flask import Flask, render_template, request, flash, redirect, url_for
from config import Config
from models import db, Stock, Balance
from stock_service import StockService
from dotenv import load_dotenv
import os

# Import env variables so keys are available
load_dotenv()
 
# Iniitialize flask app and import config class with keys
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database, route is kept on config file
db.init_app(app)

# Routing for home page, pulls user db info, loading owned stocks and portfolio balance, routes to index.html
@app.route("/")
def index():
    stock = Stock.query.first()
    balance = Balance.query.first()
    if not stock or not balance:
        flash('No stock or balance data available.', 'danger')
    return render_template('index.html', stock=stock, balance=balance)

# Routing for trade page, with get and post methods, for submitting the search form. Loads the trade.html page. Prepares stock ticker entry for proper format and validates.
# Redirects to stock_details.html page with valid input.
@app.route("/trade", methods = ['GET', 'POST'])
def trade():
    if request.method == 'POST' and request.form.get('action') == 'search':
        symbol = request.form.get('symbol').upper().strip()
        if not symbol.isalpha():
            flash('Invalid stock symbol. Please enter a valid symbol.', 'danger')
            return redirect(url_for('trade'))
        return redirect(url_for('stock_details', symbol=symbol))
    return render_template('trade.html')

# Routing for search form, with symbol validation. Redirects to stock_details.html.
@app.route("/search", methods=['POST'])
def search():
    symbol = request.form.get('symbol').upper()
    return redirect(url_for('stock_details', symbol=symbol))

# Routing to help.html page.
@app.route("/help")
def help():
    return render_template('help.html')

# Routing for stock_details page, populates the URL with the passed stock symbol. Error handling set up for invalid stock input, which returns to trade page.
@app.route("/stock/<symbol>")
def stock_details(symbol):
    try:
        price = StockService.get_stock_price(symbol)
        if price is None:
            flash(f'Failed to fetch price for stock {symbol}. Please try again.', 'danger')
            return redirect(url_for('trade'))
    except Exception as e:
        flash(f'Error fetching stock ticker: {e}', 'danger')
        return redirect(url_for('trade'))
    return render_template('stock_details.html', symbol=symbol, price=price)

# Routing for buy form. Queries database to see if stock exists there to add to user account, otherwise it creates a new entry. Updates quantity owned, price,
# and user balance. Error handling is set up to ensure you cannot buy more than balance in account, the stock is valid, and error with entering data does not
# break the process.
@app.route("/buy", methods=['POST'])
def buy():
    symbol = request.form.get('symbol')
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        stock = Stock(symbol=symbol, quantity=0, purchase_price=0)
    quantity = int(request.form.get('quantity'))
    if quantity <= 0:
        flash('Invalid quantity. Please enter a positive integer.', 'danger')
        return redirect(url_for('stock_details', symbol=symbol))
    try:
        stock.purchase_price = StockService.get_stock_price(symbol)
        if stock.purchase_price is None:
            flash(f'Invalid stock symbol {symbol}. Please enter a valid symbol.', 'danger')
            return redirect(url_for('stock_details', symbol=symbol))
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
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing transaction: {e}', 'danger')
    return redirect(url_for('trade'))

# Routing for sell form. Queries database to see if stock exists. Updates quantity owned, price, and user balance. Error handling is set up to ensure
# you cannot sell more than quantity in account, the stock is valid, and error with entering data does not break the process.
@app.route("/sell", methods=['POST'])
def sell():
    symbol = request.form.get('symbol')
    stock = Stock.query.filter_by(symbol=symbol).first()
    if stock:
        balance = Balance.query.first()
        quantity = int(request.form.get('quantity'))
        if quantity <= 0:
            flash('Invalid quantity. Please enter a positive integer.', 'danger')
            return redirect(url_for('stock_details', symbol=symbol))
        try:
            if stock.quantity >= quantity:
                curr_price = StockService.get_stock_price(symbol)
                stock.purchase_price = curr_price
                stock.quantity -= quantity
                balance.amount += quantity * stock.purchase_price
                db.session.commit()
                flash(f'Sold {quantity} shares of {stock.symbol}!', 'success')
            else:
                flash('Not enough shares to sell!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing transaction: {e}', 'danger')
    else:
        flash(f'Stock {symbol} not found in portfolio!', 'danger')
    return redirect(url_for('trade'))

# Routing to error 404 page, for invalid user route
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Routing to error 500 page, for invalid web app response
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == "__main__":
    with app.app_context():
        db.drop_all() #drop tables at beginning for development, remove for persistence
        db.create_all()
        if not Stock.query.first():
            try:
                price = StockService.get_stock_price('AAPL')
                stock = Stock(symbol="AAPL", purchase_price=price, quantity=1)
                db.session.add(stock)
                db.session.add(Balance(amount=10000.00))
                db.session.commit()
            except Exception as e:
                print(f"Error initializing the database: {e}")
    app.run(debug=True)
