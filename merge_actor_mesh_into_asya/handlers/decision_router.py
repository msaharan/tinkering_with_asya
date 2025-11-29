"""
Asya-compatible DecisionRouter.

Translates the actor-mesh decision routing logic to envelope mode handlers:
- Reads envelope["payload"] enrichments
- Mutates envelope["route"]["actors"] (future steps only)
- Advances route["current"] so the sidecar sends to the next actor
"""

import logging
from typing import Any, Dict, List, Optional


class DecisionRouter:
    # Actor names are DNS-safe for Kubernetes and queue naming
    RESPONSE_GENERATOR = "response-generator"
    RESPONSE_AGGREGATOR = "response-aggregator"
    ESCALATION_ROUTER = "escalation-router"
    EXECUTION_COORDINATOR = "execution-coordinator"
    CONTEXT_RETRIEVER = "context-retriever"

    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger("asya.decision-router")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level.upper())

    def process(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        payload = envelope.get("payload") or {}
        route = envelope.get("route") or {}
        actors = list(route.get("actors") or [])
        current = int(route.get("current", 0))

        self._validate_route(actors, current)
        route["actors"] = actors

        sentiment = payload.get("sentiment") or {}
        intent = payload.get("intent") or {}
        context = payload.get("context") or {}

        self._make_routing_decisions(route, current, sentiment, intent, context)
        self._advance_pointer(route, current)
        return envelope

    def _validate_route(self, actors: List[str], current: int) -> None:
        if not actors:
            raise RuntimeError("DecisionRouter requires a non-empty route.actors list.")
        if current < 0 or current >= len(actors):
            raise RuntimeError(f"route.current {current} is out of bounds for actors list of length {len(actors)}.")

    def _make_routing_decisions(
        self,
        route: Dict[str, Any],
        current: int,
        sentiment: Dict[str, Any],
        intent: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        changes: Dict[str, Any] = {}

        if self._should_escalate_immediately(sentiment, intent, context):
            changes["immediate_escalation"] = True
            self._override_future(route, current, [self.ESCALATION_ROUTER, self.RESPONSE_AGGREGATOR])
            self.logger.info("Immediate escalation triggered; rerouting to escalation flow.")
            return changes

        if self._needs_priority_processing(sentiment, intent):
            changes["priority_processing"] = True
            self._insert_priority_steps(route, current)

        if self._needs_action_execution(intent, context):
            changes["action_execution"] = True
            self._ensure_execution_coordinator(route, current)

        if self._has_low_confidence(intent):
            changes["low_confidence"] = True
            self._add_human_review(route, current)

        if self._is_complex_query(intent, context):
            changes["complex_processing"] = True
            self._add_enhanced_processing(route, current)

        if changes:
            self.logger.debug("Applied routing changes: %s", changes)

        return changes

    def _should_escalate_immediately(
        self, sentiment: Dict[str, Any], intent: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        if sentiment.get("urgency") == "critical":
            return True
        if sentiment.get("sentiment") == "negative" and sentiment.get("intensity", 0) > 0.8:
            return True

        intent_type = intent.get("intent", "")
        if intent_type in {"legal_threat", "formal_complaint", "regulatory_complaint"}:
            return True

        customer_tier = (context.get("customer") or {}).get("tier", "")
        if customer_tier == "VIP" and sentiment.get("urgency") in {"high", "critical"}:
            return True

        return False

    def _needs_priority_processing(self, sentiment: Dict[str, Any], intent: Dict[str, Any]) -> bool:
        if sentiment.get("urgency") == "high":
            return True
        intent_type = intent.get("intent", "")
        return intent_type in {"billing_inquiry", "refund_request", "payment_issue"}

    def _needs_action_execution(self, intent: Dict[str, Any], context: Dict[str, Any]) -> bool:
        intent_type = intent.get("intent", "")
        actionable_intents = {
            "refund_request",
            "order_modification",
            "shipping_change",
            "billing_update",
            "account_update",
            "order_cancellation",
        }
        return intent_type in actionable_intents

    def _has_low_confidence(self, intent: Dict[str, Any]) -> bool:
        return float(intent.get("confidence", 1.0)) < 0.6

    def _is_complex_query(self, intent: Dict[str, Any], context: Dict[str, Any]) -> bool:
        intent_type = intent.get("intent", "")
        complex_intents = {"technical_support", "product_compatibility", "bulk_order"}
        orders = context.get("orders") or []
        if len(orders) > 5:
            return True
        return intent_type in complex_intents

    def _override_future(self, route: Dict[str, Any], current: int, new_tail: List[str]) -> None:
        prefix = route["actors"][: current + 1]
        route["actors"] = prefix + new_tail

    def _insert_priority_steps(self, route: Dict[str, Any], current: int) -> None:
        next_steps = route["actors"][current + 1 :]
        if self.RESPONSE_GENERATOR not in next_steps[:2]:
            route["actors"].insert(current + 1, self.RESPONSE_GENERATOR)

    def _ensure_execution_coordinator(self, route: Dict[str, Any], current: int) -> None:
        actors = route["actors"]
        if self.EXECUTION_COORDINATOR in actors:
            return
        response_idx = self._find_step_index(actors, self.RESPONSE_GENERATOR)
        if response_idx is not None and response_idx > current:
            actors.insert(response_idx, self.EXECUTION_COORDINATOR)
        else:
            actors.append(self.EXECUTION_COORDINATOR)

    def _add_human_review(self, route: Dict[str, Any], current: int) -> None:
        actors = route["actors"]
        if self.ESCALATION_ROUTER in actors:
            return
        aggregator_idx = self._find_step_index(actors, self.RESPONSE_AGGREGATOR)
        if aggregator_idx is not None and aggregator_idx > current:
            actors.insert(aggregator_idx, self.ESCALATION_ROUTER)
        else:
            actors.append(self.ESCALATION_ROUTER)

    def _add_enhanced_processing(self, route: Dict[str, Any], current: int) -> None:
        remaining_steps = route["actors"][current + 1 :]
        if self.CONTEXT_RETRIEVER not in remaining_steps:
            route["actors"].insert(current + 1, self.CONTEXT_RETRIEVER)

    def _find_step_index(self, steps: List[str], step_name: str) -> Optional[int]:
        try:
            return steps.index(step_name)
        except ValueError:
            return None

    def _advance_pointer(self, route: Dict[str, Any], current: int) -> None:
        next_index = current + 1
        if next_index >= len(route["actors"]):
            route["current"] = len(route["actors"]) - 1
        else:
            route["current"] = next_index
