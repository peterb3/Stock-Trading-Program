from polygon import RESTClient
import os

class StockService:
    API_KEY = os.environ.get('STOCK_API_KEY')

    @staticmethod
    def get_stock_price(symbol):
        client = RESTClient(StockService.API_KEY)
        
        last_trade = client.get_last_trade(symbol,)

        return last_trade.price
