from __future__ import annotations
from abc import ABC, abstractmethod

from trading.builder import TradingProcessBuilder
from trading.state import TradingState


class TradingProcess(ABC):
    """Abstract base class for trading processes.
    Each subclass uses the Builder to construct its own LangGraph state graph."""

    def __init__(self, builder: TradingProcessBuilder):
        self._builder = builder
        self._compiled_graph = None
        self.process_type: str = ""

    @abstractmethod
    def build_graph(self) -> None:
        """Use the builder to construct the state graph."""
        ...

    def run(self, initial_state: TradingState) -> TradingState:
        """Execute the compiled graph with the given initial state."""
        if not self._compiled_graph:
            self.build_graph()
        return self._compiled_graph.invoke(initial_state)


class ConventionalProcess(TradingProcess):
    """Conventional trading: START -> Research -> Picked? -> Trade -> END
    Single research step followed by a single trade."""

    def __init__(self, builder: TradingProcessBuilder):
        super().__init__(builder)
        self.process_type = "conventional"

    def build_graph(self) -> None:
        self._compiled_graph = (
            self._builder
                .create_graph()
                .add_research_node()
                .add_trade_node()
                .set_entry("research")
                .add_research_decision()
                .add_trade_to_end()
                .build()
        )


class IncrementalProcess(TradingProcess):
    """Iterative incremental trading: START -> Research -> Picked? ->
    Trade -> Assess -> Next Increment? -> loop or END."""

    def __init__(self, builder: TradingProcessBuilder):
        super().__init__(builder)
        self.process_type = "incremental"

    def build_graph(self) -> None:
        self._compiled_graph = (
            self._builder
                .create_graph()
                .add_research_node()
                .add_trade_node()
                .add_assess_node()
                .set_entry("research")
                .add_research_decision()
                .add_trade_to_assess()
                .add_assess_decision()
                .build()
        )
