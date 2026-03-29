class Balance:
    """Expert pattern: Balance has the information about available
    funds, so it is the expert for fund-related decisions."""

    def __init__(self, amount: float = 100_000.0):
        self.amount = amount

    def has_funds(self, amount: float) -> bool:
        return self.amount >= amount

    def deduct(self, amount: float):
        if not self.has_funds(amount):
            raise ValueError(f"Insufficient funds: need ${amount:.2f}, have ${self.amount:.2f}")
        self.amount -= amount

    def add_funds(self, amount: float):
        self.amount += amount

    def __repr__(self) -> str:
        return f"Balance(${self.amount:,.2f})"
