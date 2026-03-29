class Rating:
    """Represents a stock rating: buy, sell, or hold."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

    def __init__(self, value: str):
        if value not in (self.BUY, self.SELL, self.HOLD):
            raise ValueError(f"Invalid rating: {value}. Must be buy, sell, or hold.")
        self.value = value

    def __repr__(self) -> str:
        return f"Rating({self.value})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Rating):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False
