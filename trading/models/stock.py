class Stock:
    """Represents a stock with a ticker symbol and current price."""

    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price
        self.previous_price = price

    def update_price(self, new_price: float):
        self.previous_price = self.price
        self.price = round(new_price, 2)

    def price_change_pct(self) -> float:
        if self.previous_price == 0:
            return 0.0
        return ((self.price - self.previous_price) / self.previous_price) * 100

    def __repr__(self) -> str:
        return f"Stock({self.symbol}, ${self.price:.2f})"
