import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'your_secret_key'
    STOCK_API_KEY = os.environ.get('STOCK_API_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///project.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
