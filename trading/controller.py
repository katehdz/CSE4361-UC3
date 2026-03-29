from __future__ import annotations

from trading.builder import TradingProcessBuilder
from trading.processes import ConventionalProcess, IncrementalProcess, TradingProcess
from trading.state import TradingState
from trading.models.balance import Balance
from trading.models.portfolio import Portfolio
from trading.models.stock import Stock
from trading.models.trade import Trade
from trading.models.transaction import Transaction
from trading.models.watchlist import Watchlist


class TradingController:
    """Controller pattern: orchestrates the trading workflow.
    Delegates research, trading, and portfolio management to the appropriate
    components. Does not perform domain logic itself."""

    def __init__(self, watchlist: Watchlist, portfolio: Portfolio, balance: Balance):
        self._watchlist = watchlist
        self._portfolio = portfolio
        self._balance = balance
        self._builder = TradingProcessBuilder()
        self._transactions: list[Transaction] = []

    def start_process(self, process_type: str, mode: str) -> list[Transaction]:
        """Creator pattern: controller creates the right TradingProcess
        because it has the initializing data needed."""
        if process_type == "conventional":
            process: TradingProcess = ConventionalProcess(self._builder)
        else:
            process = IncrementalProcess(self._builder)

        initial_state: TradingState = {
            "watchlist": self._watchlist,
            "portfolio": self._portfolio,
            "balance": self._balance,
            "picks": [],
            "trades_executed": [],
            "process_type": process_type,
            "mode": mode,
            "increment_round": 0,
            "continue_increment": False,
            "remaining_quantity": 0,
            "current_trade_type": "",
            "current_stock_symbol": "",
            "price_before_trade": 0.0,
        }

        result = process.run(initial_state)

        # Update controller's references from the result
        self._portfolio = result["portfolio"]
        self._balance = result["balance"]
        new_txns = result.get("trades_executed", [])
        self._transactions.extend(new_txns)

        return new_txns

    def execute_trade(self, stock: Stock, trade_type: str) -> Transaction | None:
        """Execute a single trade directly (per Step 10 design class diagram).
        Validates and executes a buy or sell for the given stock."""
        if trade_type == "buy":
            trade = Trade.create_buy(stock)
        elif trade_type == "sell":
            trade = Trade.create_sell_all(stock, self._portfolio)
        else:
            return None

        if trade.validate_trade(self._portfolio, self._balance, self._watchlist):
            txn = trade.execute_trade(self._portfolio, self._balance)
            self._transactions.append(txn)
            return txn
        return None

    @property
    def watchlist(self) -> Watchlist:
        return self._watchlist

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    @property
    def balance(self) -> Balance:
        return self._balance

    @property
    def transactions(self) -> list[Transaction]:
        return self._transactions
