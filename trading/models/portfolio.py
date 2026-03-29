from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trading.models.stock import Stock
    from trading.models.watchlist import Watchlist
    from trading.models.balance import Balance


class Portfolio:
    """Expert pattern: Portfolio has the information needed to
    calculate total value and enforce the 10% max holding rule."""

    def __init__(self):
        self._holdings: dict[str, int] = {}  # symbol -> quantity

    def add_stock(self, symbol: str, quantity: int):
        self._holdings[symbol] = self._holdings.get(symbol, 0) + quantity

    def remove_stock(self, symbol: str, quantity: int | None = None):
        if symbol not in self._holdings:
            return
        if quantity is None or quantity >= self._holdings[symbol]:
            del self._holdings[symbol]
        else:
            self._holdings[symbol] -= quantity

    def get_quantity(self, symbol: str) -> int:
        return self._holdings.get(symbol, 0)

    def get_holdings(self) -> dict[str, int]:
        return dict(self._holdings)

    def calculate_value(self, watchlist: Watchlist) -> float:
        """Only Portfolio has holding quantities, so it is the
        expert for value calculation."""
        total = 0.0
        for symbol, qty in self._holdings.items():
            stock = watchlist.get_stock(symbol)
            if stock:
                total += stock.price * qty
        return total

    def calculate_total_value(self, watchlist: Watchlist, balance: Balance) -> float:
        return self.calculate_value(watchlist) + balance.amount

    def check_max_holding(self, symbol: str, additional_qty: int,
                          watchlist: Watchlist, balance: Balance) -> bool:
        """Expert: enforces 10% rule using its own data.
        Returns True if adding additional_qty would keep the stock under 10%."""
        stock = watchlist.get_stock(symbol)
        if not stock:
            return False

        total_portfolio_value = self.calculate_total_value(watchlist, balance)
        current_qty = self.get_quantity(symbol)
        new_value = (current_qty + additional_qty) * stock.price
        max_allowed = total_portfolio_value * 0.10

        return new_value <= max_allowed

    def __repr__(self) -> str:
        return f"Portfolio({len(self._holdings)} stocks)"
