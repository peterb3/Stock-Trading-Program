import requests
from dotenv import load_dotenv
import os

# import stock API key from env file
load_dotenv()

class StockService:
    # set API key in class
    API_KEY = os.environ.get('STOCK_API_KEY')

    # call stockdata.org API endpoint for stock symbol, pull data from JSON response, and return price as float.
    @staticmethod
    def get_stock_price(symbol):
        url = f"https://api.stockdata.org/v1/data/quote?symbols={symbol}&api_token={StockService.API_KEY}"
        
        response = requests.get(url)
        data = response.json()

        return float(data['data'][0]['price'])
