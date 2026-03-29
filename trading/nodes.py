from __future__ import annotations
import math

from trading.state import TradingState
from trading.research import Research
from trading.models.trade import Trade
from trading.models.rating import Rating
from trading.simulation import update_prices


def research_node(state: TradingState) -> dict:
    """LangGraph node: evaluates stocks and picks one to trade."""
    research = Research()
    picks = research.evaluate_stocks(
        state["watchlist"], state["portfolio"], state["mode"]
    )
    return {"picks": picks}


def trade_node(state: TradingState) -> dict:
    """LangGraph node: executes a trade based on the research pick.
    Handles both initial trades and incremental continuation trades."""
    picks = state["picks"]
    if not picks:
        return {"trades_executed": state["trades_executed"]}

    stock, rating = picks[0]
    portfolio = state["portfolio"]
    balance = state["balance"]
    watchlist = state["watchlist"]
    process_type = state["process_type"]
    transactions = list(state["trades_executed"])

    # Check if this is a continuation trade (incremental loop)
    remaining = state.get("remaining_quantity", 0)
    is_continuation = remaining > 0 and state.get("continue_increment", False)

    if is_continuation:
        # Continuation: trade the next 1/3 of remaining shares
        symbol = state["current_stock_symbol"]
        trade_type = state["current_trade_type"]
        cont_stock = watchlist.get_stock(symbol)
        if not cont_stock:
            return {"trades_executed": transactions, "continue_increment": False}

        partial_qty = max(1, math.ceil(remaining / 3))
        trade = Trade(cont_stock, trade_type, partial_qty)

        if trade.validate_trade(portfolio, balance, watchlist):
            txn = trade.execute_trade(portfolio, balance)
            transactions.append(txn)
            new_remaining = remaining - partial_qty
            return {
                "trades_executed": transactions,
                "portfolio": portfolio,
                "balance": balance,
                "remaining_quantity": new_remaining,
                "price_before_trade": cont_stock.price,
                "increment_round": state["increment_round"] + 1,
            }
        return {"trades_executed": transactions, "continue_increment": False}

    # Initial trade
    if rating.value == Rating.BUY:
        if process_type == "incremental":
            full_qty = math.floor(Trade.BUY_AMOUNT / stock.price)
            if full_qty < 1:
                full_qty = 1
            partial_qty = max(1, math.ceil(full_qty / 3))
            trade = Trade(stock, "buy", partial_qty)
            remaining = full_qty - partial_qty
        else:
            trade = Trade.create_buy(stock)
            remaining = 0

        if trade.validate_trade(portfolio, balance, watchlist):
            txn = trade.execute_trade(portfolio, balance)
            transactions.append(txn)
            return {
                "trades_executed": transactions,
                "portfolio": portfolio,
                "balance": balance,
                "remaining_quantity": remaining,
                "current_trade_type": "buy",
                "current_stock_symbol": stock.symbol,
                "price_before_trade": stock.price,
                "increment_round": 1,
            }

    elif rating.value == Rating.SELL:
        held = portfolio.get_quantity(stock.symbol)
        if held <= 0:
            return {"trades_executed": transactions}

        if process_type == "incremental":
            partial_qty = max(1, math.ceil(held / 3))
            trade = Trade(stock, "sell", partial_qty)
            remaining = held - partial_qty
        else:
            trade = Trade.create_sell_all(stock, portfolio)
            remaining = 0

        if trade.validate_trade(portfolio, balance, watchlist):
            txn = trade.execute_trade(portfolio, balance)
            transactions.append(txn)
            return {
                "trades_executed": transactions,
                "portfolio": portfolio,
                "balance": balance,
                "remaining_quantity": remaining,
                "current_trade_type": "sell",
                "current_stock_symbol": stock.symbol,
                "price_before_trade": stock.price,
                "increment_round": 1,
            }

    return {"trades_executed": transactions}


def assess_node(state: TradingState) -> dict:
    """LangGraph node: assesses whether to continue incremental trading.
    Only checks the price threshold — does NOT execute trades.
    Simulates a price update to evaluate market movement."""
    remaining = state.get("remaining_quantity", 0)

    if remaining <= 0:
        return {"continue_increment": False, "remaining_quantity": 0}

    watchlist = state["watchlist"]
    symbol = state["current_stock_symbol"]
    trade_type = state["current_trade_type"]
    price_before = state["price_before_trade"]

    # Simulate price movement for assessment
    update_prices(watchlist)

    stock = watchlist.get_stock(symbol)
    if not stock:
        return {"continue_increment": False}

    current_price = stock.price
    change_pct = ((current_price - price_before) / price_before) * 100

    if trade_type == "buy":
        # Continue buying if price went up but within 1%
        should_continue = 0 < change_pct <= 1.0
    else:
        # Continue selling if price went down but within 1%
        should_continue = -1.0 <= change_pct < 0

    return {
        "continue_increment": should_continue,
        "price_before_trade": current_price,
    }


# --- Conditional edge functions ---

def stocks_picked(state: TradingState) -> str:
    """Router: go to trade if a stock was picked, else end."""
    if state["picks"]:
        return "trade"
    return "end"


def next_increment(state: TradingState) -> str:
    """Router: loop back to trade if continuing, else end."""
    if state.get("continue_increment", False) and state.get("remaining_quantity", 0) > 0:
        return "trade"
    return "end"
