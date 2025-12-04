"""
Asya-compatible IntentAnalyzer in payload mode.

Provides a lightweight, offline intent and entity extractor that mirrors the
Actor Mesh demo behaviour without external dependencies. Returns the payload
with a new ``intent`` key describing the detected intent, extracted entities,
and confidence score.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO)


class IntentAnalyzer:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Simple keyword maps to approximate the original intent set
        self.intent_rules: List[Tuple[str, List[str]]] = [
            ("refund_request", ["refund", "money back", "return", "exchange"]),
            ("delivery_issue", ["late", "delayed", "delay", "where is", "arrive", "delivery"]),
            ("product_issue", ["broken", "defect", "damaged", "not working", "faulty"]),
            ("billing_issue", ["charge", "charged", "billing", "payment", "invoice"]),
            ("cancellation_request", ["cancel", "stop", "wrong order", "do not ship"]),
            ("account_issue", ["login", "password", "account", "profile"]),
            ("escalation_request", ["manager", "supervisor", "human"]),
        ]

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Detect intent and entities, then append them to the payload."""
        try:
            message = str(payload.get("customer_message") or "")
            lowered = message.lower()

            intent, matched_keywords = self._detect_intent(lowered)
            entities = self._extract_entities(message)
            confidence = self._calculate_confidence(matched_keywords, entities)

            intent_result: Dict[str, Any] = {
                "intent": intent,
                "entities": entities,
                "confidence": confidence,
                "analysis_method": "rule_based",
                "matched_keywords": matched_keywords,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }

            self.logger.info(
                "Intent detected: %s (confidence %.2f) entities=%s",
                intent,
                confidence,
                list(entities.keys()) or "none",
            )

            return {**payload, "intent": intent_result}

        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Intent analysis failed: %s", exc)
            fallback = {
                "intent": "general_inquiry",
                "entities": {},
                "confidence": 0.25,
                "analysis_method": "error_fallback",
                "error": str(exc),
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
            return {**payload, "intent": fallback}

    def _detect_intent(self, lowered_message: str) -> Tuple[str, List[str]]:
        """Return best-matching intent and the keywords that triggered it."""
        best_intent = "general_inquiry"
        best_hits: List[str] = []

        for intent, keywords in self.intent_rules:
            hits = [kw for kw in keywords if kw in lowered_message]
            if len(hits) > len(best_hits):
                best_intent = intent
                best_hits = hits

        return best_intent, best_hits

    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract simple entities such as order numbers, emails, and tracking ids."""
        entities: Dict[str, Any] = {}

        order_match = re.search(r"\b(?:order|#|no\.?)\s*(\d{5,})\b", message, re.IGNORECASE)
        if order_match:
            entities["order_number"] = order_match.group(1)

        tracking_match = re.search(r"\b1Z[0-9A-Z]{10,}\b", message)
        if tracking_match:
            entities["tracking_id"] = tracking_match.group(0)

        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", message)
        if email_match:
            entities["email"] = email_match.group(0)

        return entities

    def _calculate_confidence(self, matched_keywords: List[str], entities: Dict[str, Any]) -> float:
        """Heuristic confidence score based on signals seen."""
        base = 0.35
        base += 0.1 * min(len(matched_keywords), 3)
        if entities:
            base += 0.1
        return float(min(base, 0.95))
