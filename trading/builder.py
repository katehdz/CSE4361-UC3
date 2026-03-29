from __future__ import annotations

from langgraph.graph import StateGraph, END

from trading.state import TradingState
from trading.nodes import (
    research_node,
    trade_node,
    assess_node,
    stocks_picked,
    next_increment,
)


class TradingProcessBuilder:
    """Builder pattern: constructs a LangGraph StateGraph step by step.
    Uses a fluent interface (method chaining) where each method returns self."""

    def __init__(self):
        self._graph: StateGraph | None = None

    def create_graph(self) -> TradingProcessBuilder:
        """Step 1: Initialize a fresh StateGraph."""
        self._graph = StateGraph(TradingState)
        return self

    def add_research_node(self) -> TradingProcessBuilder:
        """Step 2: Add the research node."""
        self._graph.add_node("research", research_node)
        return self

    def add_trade_node(self) -> TradingProcessBuilder:
        """Step 3: Add the trade node."""
        self._graph.add_node("trade", trade_node)
        return self

    def add_assess_node(self) -> TradingProcessBuilder:
        """Step 4 (incremental only): Add the assess node."""
        self._graph.add_node("assess", assess_node)
        return self

    def set_entry(self, node: str) -> TradingProcessBuilder:
        """Set the entry point of the graph."""
        self._graph.set_entry_point(node)
        return self

    def add_research_decision(self) -> TradingProcessBuilder:
        """Add conditional edge: research -> trade or end."""
        self._graph.add_conditional_edges(
            "research",
            stocks_picked,
            {"trade": "trade", "end": END},
        )
        return self

    def add_trade_to_end(self) -> TradingProcessBuilder:
        """Add edge: trade -> END (conventional process)."""
        self._graph.add_edge("trade", END)
        return self

    def add_trade_to_assess(self) -> TradingProcessBuilder:
        """Add edge: trade -> assess (incremental process)."""
        self._graph.add_edge("trade", "assess")
        return self

    def add_assess_decision(self) -> TradingProcessBuilder:
        """Add conditional edge: assess -> trade (loop) or end."""
        self._graph.add_conditional_edges(
            "assess",
            next_increment,
            {"trade": "trade", "end": END},
        )
        return self

    def build(self):
        """Final step: compile the graph and return the runnable."""
        return self._graph.compile()
