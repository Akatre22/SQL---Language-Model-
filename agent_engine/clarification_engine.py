"""
Ambiguity Detection & Clarification Decision Engine for SQL-SLM (Item 17).
Intercepts underspecified or ambiguous queries and generates structured clarification
payloads to prevent hallucinations and ensure safe, deterministic execution.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ClarificationResult:
    is_ambiguous: bool
    ambiguity_type: Optional[str] = None
    clarification_message: Optional[str] = None
    suggested_options: List[str] = field(default_factory=list)

class ClarificationEngine:
    def __init__(self):
        # Ambiguity Pattern Rules
        self.ranking_pattern = re.compile(r"\b(?:best|top|worst|most\s+popular|highest\s+performing|star)\s+(?:customers?|clients?|products?|employees?|items?)\b", re.IGNORECASE)
        self.temporal_pattern = re.compile(r"\b(?:recent|recently|latest|newest|current)\s+(?:orders?|transactions?|signups?|shipments?|records?)\b", re.IGNORECASE)
        self.grain_pattern = re.compile(r"\b(?:show|give\s+me|provide|get)\s+(?:sales|revenue|payroll|performance)\s+(?:summary|breakdown|stats?|numbers?|metrics?)\b", re.IGNORECASE)
        self.status_pattern = re.compile(r"\b(?:active|valid|good|qualified)\s+(?:accounts?|loans?|leads?|users?)\b", re.IGNORECASE)

    def extract_model_clarification(self, model_output: str) -> Optional[str]:
        """Extracts structured text enclosed in <clarify> ... </clarify> tags."""
        match = re.search(r"<clarify>\s*([\s\S]*?)\s*(?:</clarify>|<\|endoftext\|>|$)", model_output, re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip()
        return None

    def analyze_query(self, user_query: str) -> ClarificationResult:
        """
        Analyzes a natural language query for ambiguity indicators.
        Returns ClarificationResult indicating whether user confirmation is required.
        """
        q_clean = user_query.strip()

        # 1. Check Missing Ranking Metric
        if self.ranking_pattern.search(q_clean) and not any(w in q_clean.lower() for w in ["by", "salary", "amount", "total", "price", "spend", "balance"]):
            return ClarificationResult(
                is_ambiguous=True,
                ambiguity_type="MISSING_RANKING_METRIC",
                clarification_message="The ranking metric is underspecified. Please specify how 'top / best' should be evaluated:",
                suggested_options=[
                    "Rank by total monetary spending / revenue",
                    "Rank by total transaction count / order frequency",
                    "Rank by customer tenure / join date"
                ]
            )

        # 2. Check Missing Temporal Window
        if self.temporal_pattern.search(q_clean) and not any(w in q_clean.lower() for w in ["days", "months", "2023", "2024", "today", "yesterday", "week"]):
            return ClarificationResult(
                is_ambiguous=True,
                ambiguity_type="MISSING_TIME_WINDOW",
                clarification_message="The recency timeframe is ambiguous. Please select a time window:",
                suggested_options=[
                    "Past 24 hours",
                    "Past 7 days",
                    "Past 30 days",
                    "Current calendar month"
                ]
            )

        # 3. Check Missing Aggregation Grain
        if self.grain_pattern.search(q_clean) and not any(w in q_clean.lower() for w in ["by", "group", "per", "region", "department", "category"]):
            return ClarificationResult(
                is_ambiguous=True,
                ambiguity_type="MISSING_AGGREGATION_GRAIN",
                clarification_message="The aggregation dimension is unspecified. Please choose how to group the summary:",
                suggested_options=[
                    "Group by Region",
                    "Group by Product Category",
                    "Group by Month"
                ]
            )

        # 4. Check Ambiguous Status Filter
        if self.status_pattern.search(q_clean) and not any(w in q_clean.lower() for w in ["status", "where", "balance", ">", "="]):
            return ClarificationResult(
                is_ambiguous=True,
                ambiguity_type="AMBIGUOUS_STATUS_FILTER",
                clarification_message="The qualification criteria is ambiguous. Please define the filter condition:",
                suggested_options=[
                    "Explicit status = 'ACTIVE'",
                    "Balance > 0 with activity in last 90 days",
                    "Non-delinquent accounts"
                ]
            )

        return ClarificationResult(is_ambiguous=False)

if __name__ == "__main__":
    engine = ClarificationEngine()
    test_queries = [
        "Show me the top customers",
        "Show recent orders",
        "Give me sales summary",
        "Show customers from EMEA region with spending over 1000"  # Specific query
    ]
    print("[*] Testing Ambiguity Decision Engine:")
    for tq in test_queries:
        res = engine.analyze_query(tq)
        print(f"\nQuery: '{tq}'")
        print(f"  -> Ambiguous: {res.is_ambiguous} (Type: {res.ambiguity_type})")
        if res.is_ambiguous:
            print(f"  -> Message: {res.clarification_message}")
            print(f"  -> Options: {res.suggested_options}")
