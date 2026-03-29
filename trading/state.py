from __future__ import annotations
from typing import TypedDict

from trading.models.balance import Balance
from trading.models.portfolio import Portfolio
from trading.models.rating import Rating
from trading.models.stock import Stock
from trading.models.transaction import Transaction
from trading.models.watchlist import Watchlist


class TradingState(TypedDict):
    """Shared state flowing through LangGraph nodes."""
    watchlist: Watchlist
    portfolio: Portfolio
    balance: Balance
    picks: list[tuple[Stock, Rating]]
    trades_executed: list[Transaction]
    process_type: str       # "conventional" or "incremental"
    mode: str               # "auto" or "manual"
    # Incremental process fields
    increment_round: int
    continue_increment: bool
    remaining_quantity: int
    current_trade_type: str  # "buy" or "sell" for incremental tracking
    current_stock_symbol: str
    price_before_trade: float
