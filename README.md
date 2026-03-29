# CSE4361-UC3 — Trade Stocks

Simulated stock-trading application for CSE 4361 (Software Design Patterns) — Group H.

Implements two trading processes using **LangGraph** state graphs and demonstrates the **Controller**, **Expert**, **Creator**, and **Builder** design patterns.

## Prerequisites

- Python 3.10+
- pip

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd CSE4361-UC3
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

```bash
python main.py [OPTIONS]
```

### Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--process` | `conventional`, `incremental` | `conventional` | Trading process type |
| `--mode` | `auto`, `manual` | `auto` | Auto (heuristic AI) or manual (CLI prompts) |
| `--cycles` | integer | `0` (infinite) | Number of trading cycles to run |

### Examples

```bash
# Run conventional process in auto mode (infinite cycles, Ctrl+C to stop)
python main.py --process conventional --mode auto

# Run incremental process for 5 cycles
python main.py --process incremental --mode auto --cycles 5

# Manual mode — you pick which stocks to buy/sell each cycle
python main.py --process conventional --mode manual

# Incremental + manual
python main.py --process incremental --mode manual --cycles 3
```

## How It Works

1. The system starts with **$100,000** in funds and a watchlist of 10 stocks (AAPL, AMGN, XOM, GS, NVDA, ISRG, MSFT, MRK, CCL, NFLX).
2. Every **10 seconds**, stock prices fluctuate randomly (-5% to +5%).
3. Each cycle runs a **Research** phase (evaluate stocks, pick one to buy or sell) followed by a **Trade** phase.
4. **Conventional process**: buys $5,000 of a stock at once, or sells all shares.
5. **Incremental process**: buys/sells in 1/3 increments, reassessing price movement (within 1% threshold) after each partial trade.

### Constraints

- Max buy per pick: $5,000
- Max holding per stock: 10% of total portfolio value
- Balance cannot go negative

## Design Patterns

| Pattern | Class(es) | Role |
|---------|-----------|------|
| **Controller** | `TradingController` | Orchestrates the trading cycle; delegates to other components |
| **Expert** | `Portfolio`, `Balance`, `Trade`, `Research` | Each class owns the data needed for its decisions |
| **Creator** | `Watchlist` → `Stock`, `Controller` → `TradingProcess`, `Trade` → `Transaction` | Objects are created by the class that has the initialization data |
| **Builder** | `TradingProcessBuilder` | Constructs LangGraph `StateGraph` step-by-step with a fluent API |

## Project Structure

```
CSE4361-UC3/
├── main.py                        # Entry point, CLI, simulation loop
├── requirements.txt               # Python dependencies
├── trading/
│   ├── controller.py              # TradingController (Controller pattern)
│   ├── builder.py                 # TradingProcessBuilder (Builder pattern)
│   ├── processes.py               # ConventionalProcess, IncrementalProcess
│   ├── state.py                   # LangGraph TradingState definition
│   ├── nodes.py                   # LangGraph node functions
│   ├── research.py                # Stock evaluation (Expert pattern)
│   ├── simulation.py              # Price simulator
│   └── models/
│       ├── stock.py               # Stock
│       ├── rating.py              # Rating (buy/sell/hold)
│       ├── balance.py             # Balance (Expert pattern)
│       ├── portfolio.py           # Portfolio (Expert pattern)
│       ├── trade.py               # Trade (Expert pattern)
│       ├── transaction.py         # Transaction record
│       └── watchlist.py           # Watchlist (Creator pattern)
```
