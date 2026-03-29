from datetime import datetime


class Transaction:
    """Records a completed trade transaction."""

    def __init__(self, trade_type: str, stock_symbol: str, quantity: int,
                 price: float, total: float):
        self.date = datetime.now()
        self.type = trade_type
        self.stock_symbol = stock_symbol
        self.quantity = quantity
        self.price = price
        self.total = total

    def record(self) -> str:
        action = "Bought" if self.type == "buy" else "Sold"
        return (f"[{self.date.strftime('%H:%M:%S')}] {action} {self.quantity} shares "
                f"of {self.stock_symbol} @ ${self.price:.2f} "
                f"(Total: ${self.total:,.2f})")

    def __repr__(self) -> str:
        return self.record()
