from __future__ import annotations
import math
from typing import TYPE_CHECKING

from trading.models.transaction import Transaction

if TYPE_CHECKING:
    from trading.models.stock import Stock
    from trading.models.portfolio import Portfolio
    from trading.models.balance import Balance
    from trading.models.watchlist import Watchlist


class Trade:
    """Expert pattern: Trade has the information (type, quantity, stock)
    needed to validate and execute itself."""

    BUY_AMOUNT = 5000.0  # $5,000 per buy

    def __init__(self, stock: Stock, trade_type: str, quantity: int):
        self.stock = stock
        self.type = trade_type  # "buy" or "sell"
        self.quantity = quantity

    def validate_trade(self, portfolio: Portfolio, balance: Balance,
                       watchlist: Watchlist) -> bool:
        """Expert: only Trade knows its own type/quantity to validate."""
        if self.type == "buy":
            cost = self.quantity * self.stock.price
            if not balance.has_funds(cost):
                return False
            if not portfolio.check_max_holding(self.stock.symbol, self.quantity,
                                               watchlist, balance):
                return False
            return True
        elif self.type == "sell":
            held = portfolio.get_quantity(self.stock.symbol)
            return held >= self.quantity
        return False

    def execute_trade(self, portfolio: Portfolio, balance: Balance) -> Transaction:
        """Expert: Trade executes itself and returns a Transaction (Creator pattern)."""
        total = self.quantity * self.stock.price

        if self.type == "buy":
            balance.deduct(total)
            portfolio.add_stock(self.stock.symbol, self.quantity)
        elif self.type == "sell":
            balance.add_funds(total)
            portfolio.remove_stock(self.stock.symbol, self.quantity)

        return Transaction(
            trade_type=self.type,
            stock_symbol=self.stock.symbol,
            quantity=self.quantity,
            price=self.stock.price,
            total=total,
        )

    @classmethod
    def create_buy(cls, stock: Stock) -> Trade:
        """Create a buy trade for $5,000 worth of the stock."""
        quantity = math.floor(cls.BUY_AMOUNT / stock.price)
        if quantity < 1:
            quantity = 1
        return cls(stock, "buy", quantity)

    @classmethod
    def create_sell_all(cls, stock: Stock, portfolio: Portfolio) -> Trade:
        """Create a sell trade for all held shares of the stock."""
        quantity = portfolio.get_quantity(stock.symbol)
        return cls(stock, "sell", quantity)

    @classmethod
    def create_partial(cls, stock: Stock, trade_type: str,
                       full_quantity: int) -> Trade:
        """Create a partial trade for ~1/3 of the given quantity."""
        partial_qty = max(1, math.ceil(full_quantity / 3))
        return cls(stock, trade_type, partial_qty)

    def __repr__(self) -> str:
        return f"Trade({self.type} {self.quantity} {self.stock.symbol})"
