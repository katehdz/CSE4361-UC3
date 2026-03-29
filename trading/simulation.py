import random

from trading.models.watchlist import Watchlist


def update_prices(watchlist: Watchlist) -> None:
    """Simulate price movement: random -5% to +5% per stock."""
    for stock in watchlist.get_stocks():
        change_pct = random.uniform(-5.0, 5.0)
        factor = 1 + (change_pct / 100.0)
        stock.update_price(stock.price * factor)
