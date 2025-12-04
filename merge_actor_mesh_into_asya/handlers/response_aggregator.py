"""
Asya-compatible ResponseAggregator in payload mode.

Collects the enriched payload, prepares a final response bundle, and marks the
resolution status. In this simplified demo the aggregator just returns the
payload with a ``final_response`` field instead of delivering over HTTP.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)


class ResponseAggregator:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate the final response and mark resolution state."""
        try:
            response_text = self._extract_response_text(payload.get("response"))
            guardrail = payload.get("guardrail_check") or {}
            execution = payload.get("execution_result") or {}
            intent_raw = payload.get("intent")
            sentiment_raw = payload.get("sentiment")

            intent_value = intent_raw.get("intent") if isinstance(intent_raw, dict) else (
                intent_raw if isinstance(intent_raw, str) else None
            )
            sentiment_value = None
            if isinstance(sentiment_raw, dict):
                sentiment_value = (sentiment_raw.get("sentiment") or {}).get("label")

            status = "resolved"
            if guardrail and not guardrail.get("pass", True):
                status = "needs_review"
            if payload.get("escalated"):
                status = "escalated"

            final_response = {
                "customer_email": payload.get("customer_email"),
                "response": response_text,
                "status": status,
                "intent": intent_value,
                "sentiment": sentiment_value,
                "guardrail": guardrail,
                "execution": execution,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }

            self.logger.info(
                "Aggregation complete status=%s guardrail_pass=%s",
                status,
                guardrail.get("pass", True),
            )

            return {**payload, "final_response": final_response}

        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Aggregation error: %s", exc)
            fallback = {
                "status": "error",
                "error": str(exc),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            return {**payload, "final_response": fallback}

    def _extract_response_text(self, response: Any) -> str:
        if isinstance(response, dict):
            return str(response.get("text") or response.get("response_text") or "")
        if response is None:
            return ""
        return str(response)
