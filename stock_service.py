import requests
from dotenv import load_dotenv
import os

load_dotenv()

class StockService:
    API_KEY = os.environ.get('STOCK_API_KEY')

    @staticmethod
    def get_stock_price(symbol):
        url = f"https://api.stockdata.org/v1/data/quote?symbols={symbol}&api_token={StockService.API_KEY}"
        
        response = requests.get(url)
        data = response.json()

        return float(data['data'][0]['price'])
