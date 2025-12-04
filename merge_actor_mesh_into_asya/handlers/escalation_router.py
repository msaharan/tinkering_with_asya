"""
Asya-compatible EscalationRouter in envelope mode.

Handles low-confidence or policy-violating cases by rewriting the route to end
at the ResponseAggregator and annotating the payload with escalation details.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


class EscalationRouter:
    RESPONSE_AGGREGATOR = "response-aggregator"

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def process(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        payload = envelope.get("payload", {})
        route = envelope.get("route", {})
        current = int(route.get("current", 0))

        reasons = self._determine_reasons(payload)
        payload["escalated"] = True
        payload["escalation_reasons"] = reasons
        payload["recovery_log"] = self._append_recovery_log(payload, reasons)

        # Re-route to finish at the aggregator
        prefix = route.get("actors", [])[: current + 1]
        route["actors"] = prefix + [self.RESPONSE_AGGREGATOR]

        self.logger.info("Escalation triggered; reasons=%s", reasons or "unspecified")
        return envelope

    def _determine_reasons(self, payload: Dict[str, Any]) -> List[str]:
        reasons: List[str] = []

        guardrail = payload.get("guardrail_check") or {}
        intent_raw = payload.get("intent")
        intent = intent_raw if isinstance(intent_raw, dict) else {}
        sentiment_raw = payload.get("sentiment")
        sentiment = sentiment_raw if isinstance(sentiment_raw, dict) else {}

        if guardrail and not guardrail.get("pass", True):
            reasons.append("guardrail_failure")

        try:
            confidence = float(intent.get("confidence", 1.0))
            if confidence < 0.6:
                reasons.append("low_confidence_intent")
        except (TypeError, ValueError):
            reasons.append("unknown_confidence")

        sentiment_label = ""
        if isinstance(sentiment, dict):
            sentiment_label = (sentiment.get("sentiment") or {}).get("label", "")
        if sentiment_label == "negative":
            reasons.append("negative_sentiment")

        if not reasons:
            reasons.append("manual_review")
        return reasons

    def _append_recovery_log(self, payload: Dict[str, Any], reasons: List[str]) -> List[Dict[str, Any]]:
        log = payload.get("recovery_log") or []
        log.append(
            {
                "actor": "escalation-router",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reasons": reasons,
            }
        )
        return log
