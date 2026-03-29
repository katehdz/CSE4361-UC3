import argparse
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from trading.controller import TradingController
from trading.models.balance import Balance
from trading.models.portfolio import Portfolio
from trading.models.watchlist import Watchlist
from trading.simulation import update_prices

console = Console()

# Initial stock prices from the assignment (March 2, 2026)
INITIAL_STOCKS = {
    "AAPL": 264.80,
    "AMGN": 382.66,
    "XOM": 154.37,
    "GS": 861.89,
    "NVDA": 182.36,
    "ISRG": 496.17,
    "MSFT": 398.30,
    "MRK": 121.17,
    "CCL": 29.30,
    "NFLX": 97.72,
}


def display_watchlist(watchlist: Watchlist):
    """Display the current watchlist prices in a rich table."""
    table = Table(title="Watchlist", box=box.ROUNDED)
    table.add_column("Symbol", style="cyan", justify="center")
    table.add_column("Price", style="green", justify="right")
    table.add_column("Change %", justify="right")

    for stock in watchlist.get_stocks():
        change = stock.price_change_pct()
        if change > 0:
            change_style = "green"
            change_str = f"+{change:.2f}%"
        elif change < 0:
            change_style = "red"
            change_str = f"{change:.2f}%"
        else:
            change_style = "white"
            change_str = "0.00%"

        table.add_row(
            stock.symbol,
            f"${stock.price:.2f}",
            f"[{change_style}]{change_str}[/{change_style}]",
        )

    console.print(table)


def display_portfolio(portfolio: Portfolio, balance: Balance, watchlist: Watchlist):
    """Display portfolio holdings and balance in a rich table."""
    holdings = portfolio.get_holdings()

    table = Table(title="Portfolio", box=box.ROUNDED)
    table.add_column("Symbol", style="cyan", justify="center")
    table.add_column("Shares", justify="right")
    table.add_column("Price", style="green", justify="right")
    table.add_column("Value", style="yellow", justify="right")

    total_holdings_value = 0.0
    for symbol, qty in holdings.items():
        stock = watchlist.get_stock(symbol)
        if stock:
            value = stock.price * qty
            total_holdings_value += value
            table.add_row(symbol, str(qty), f"${stock.price:.2f}", f"${value:,.2f}")

    if not holdings:
        table.add_row("[dim]No holdings[/dim]", "", "", "")

    console.print(table)

    total_value = total_holdings_value + balance.amount
    summary = Table(box=box.SIMPLE, show_header=False)
    summary.add_column("Label", style="bold")
    summary.add_column("Value", justify="right")
    summary.add_row("Holdings Value", f"[yellow]${total_holdings_value:,.2f}[/yellow]")
    summary.add_row("Cash Balance", f"[green]${balance.amount:,.2f}[/green]")
    summary.add_row("Total Value", f"[bold cyan]${total_value:,.2f}[/bold cyan]")
    console.print(summary)


def display_transactions(transactions):
    """Display recent transactions."""
    if not transactions:
        console.print("[dim]  No trades executed this cycle.[/dim]")
        return

    for txn in transactions:
        if txn.type == "buy":
            style = "green"
            icon = "BUY "
        else:
            style = "red"
            icon = "SELL"
        console.print(
            f"  [{style}]{icon}[/{style}] {txn.quantity} shares of "
            f"[cyan]{txn.stock_symbol}[/cyan] @ ${txn.price:.2f} "
            f"(${txn.total:,.2f})"
        )


def main():
    parser = argparse.ArgumentParser(description="Simulated Stock Trading App")
    parser.add_argument(
        "--process",
        choices=["conventional", "incremental"],
        default="conventional",
        help="Trading process type (default: conventional)",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "manual"],
        default="auto",
        help="Trading mode (default: auto)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=0,
        help="Number of cycles to run (0 = infinite, default: 0)",
    )
    args = parser.parse_args()

    # Initialize the system
    watchlist = Watchlist("Default", INITIAL_STOCKS)
    balance = Balance(100_000.0)
    portfolio = Portfolio()
    controller = TradingController(watchlist, portfolio, balance)

    console.print(Panel(
        f"[bold]Stock Trading Simulator[/bold]\n"
        f"Process: [cyan]{args.process}[/cyan] | "
        f"Mode: [cyan]{args.mode}[/cyan] | "
        f"Initial Funds: [green]$100,000.00[/green]",
        title="UC3 - Trade Stocks",
        border_style="blue",
    ))

    cycle = 0
    try:
        while True:
            cycle += 1
            if args.cycles > 0 and cycle > args.cycles:
                break

            console.rule(f"[bold blue]Cycle {cycle}[/bold blue]")

            # Display current state
            display_watchlist(controller.watchlist)
            display_portfolio(controller.portfolio, controller.balance,
                              controller.watchlist)

            # Run the trading process
            console.print(f"\n[bold]Running {args.process} process...[/bold]")
            new_txns = controller.start_process(args.process, args.mode)

            # Display results
            console.print("\n[bold]Trades this cycle:[/bold]")
            display_transactions(new_txns)

            # Show updated portfolio after trades
            if new_txns:
                console.print("\n[bold]Updated Portfolio:[/bold]")
                display_portfolio(controller.portfolio, controller.balance,
                                  controller.watchlist)

            # Wait and update prices
            if args.cycles == 0 or cycle < args.cycles:
                console.print(f"\n[dim]Waiting 10 seconds for price update...[/dim]")
                time.sleep(10)
                update_prices(controller.watchlist)

    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Trading stopped by user.[/bold yellow]")

    # Final summary
    console.print()
    console.rule("[bold green]Final Summary[/bold green]")
    display_portfolio(controller.portfolio, controller.balance, controller.watchlist)

    if controller.transactions:
        console.print(f"\n[bold]Total transactions: {len(controller.transactions)}[/bold]")
        for txn in controller.transactions:
            display_transactions([txn])


if __name__ == "__main__":
    main()
