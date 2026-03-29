from __future__ import annotations
from typing import TYPE_CHECKING

from trading.models.rating import Rating

if TYPE_CHECKING:
    from trading.models.stock import Stock
    from trading.models.watchlist import Watchlist
    from trading.models.portfolio import Portfolio


class Research:
    """Expert pattern: Research has the domain knowledge to evaluate
    stocks and assign ratings."""

    def evaluate_stocks(self, watchlist: Watchlist, portfolio: Portfolio,
                        mode: str) -> list[tuple[Stock, Rating]]:
        """Evaluate all stocks and return those rated buy or sell.
        In auto mode: heuristic-based. In manual mode: prompts user."""
        stocks = watchlist.get_stocks()
        picks: list[tuple[Stock, Rating]] = []

        if mode == "manual":
            picks = self._manual_evaluate(stocks, portfolio)
        else:
            picks = self._auto_evaluate(stocks, portfolio)

        # Return at most one pick (assignment requirement)
        if picks:
            return [picks[0]]
        return []

    def _auto_evaluate(self, stocks: list[Stock],
                       portfolio: Portfolio) -> list[tuple[Stock, Rating]]:
        """Heuristic-based evaluation using price changes."""
        picks: list[tuple[Stock, Rating]] = []

        for stock in stocks:
            rating = self.assign_rating(stock, portfolio)
            if rating.value == Rating.BUY or rating.value == Rating.SELL:
                picks.append((stock, rating))

        # Prioritize: sell signals first (risk management), then buy
        sells = [(s, r) for s, r in picks if r.value == Rating.SELL]
        buys = [(s, r) for s, r in picks if r.value == Rating.BUY]

        if sells:
            return sells
        return buys

    def assign_rating(self, stock: Stock, portfolio: Portfolio) -> Rating:
        """Heuristic rating based on price change percentage.
        - If portfolio is empty and stock not held: buy (initial diversification)
        - If price dropped > 2%: buy opportunity
        - If price rose > 3%: sell opportunity (if held)
        - Otherwise: hold
        """
        change_pct = stock.price_change_pct()
        held_qty = portfolio.get_quantity(stock.symbol)
        total_holdings = len(portfolio.get_holdings())

        # Initial buying phase: buy stocks when portfolio is small
        if total_holdings < 5 and held_qty == 0:
            return Rating(Rating.BUY)

        if held_qty > 0 and change_pct > 3.0:
            return Rating(Rating.SELL)
        elif change_pct < -2.0:
            return Rating(Rating.BUY)
        else:
            return Rating(Rating.HOLD)

    def _manual_evaluate(self, stocks: list[Stock],
                         portfolio: Portfolio) -> list[tuple[Stock, Rating]]:
        """Prompt user for ratings via CLI."""
        picks: list[tuple[Stock, Rating]] = []

        print("\n--- Manual Stock Evaluation ---")
        for stock in stocks:
            held = portfolio.get_quantity(stock.symbol)
            change = stock.price_change_pct()
            print(f"  {stock.symbol}: ${stock.price:.2f} "
                  f"(change: {change:+.2f}%, held: {held} shares)")

        print("\nEnter a stock symbol to trade (or 'skip' to skip):")
        symbol = input("  Symbol: ").strip().upper()

        if symbol == "SKIP" or not symbol:
            return []

        target = None
        for stock in stocks:
            if stock.symbol == symbol:
                target = stock
                break

        if not target:
            print(f"  Stock {symbol} not found in watchlist.")
            return []

        action = input("  Action (buy/sell): ").strip().lower()
        if action in (Rating.BUY, Rating.SELL):
            picks.append((target, Rating(action)))
        else:
            print("  Invalid action. Skipping.")

        return picks
