from trading.models.stock import Stock


class Watchlist:
    """Creator pattern: Watchlist creates Stock objects because it
    aggregates/contains them and has the initialization data."""

    def __init__(self, name: str, stock_data: dict[str, float]):
        self.name = name
        self._stocks: list[Stock] = [
            Stock(symbol, price) for symbol, price in stock_data.items()
        ]

    def get_stocks(self) -> list[Stock]:
        return list(self._stocks)

    def get_stock(self, symbol: str) -> Stock | None:
        for stock in self._stocks:
            if stock.symbol == symbol:
                return stock
        return None

    def __repr__(self) -> str:
        return f"Watchlist({self.name}, {len(self._stocks)} stocks)"
