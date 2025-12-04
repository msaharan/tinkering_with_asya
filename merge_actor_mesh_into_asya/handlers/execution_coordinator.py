"""
Asya-compatible ExecutionCoordinator in payload mode.

Simulates execution of the action plan produced earlier in the pipeline. No
external API calls are made; instead we return structured results that mirror
what the real Actor Mesh demo would emit.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


class ExecutionCoordinator:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned actions (simulated) and append results."""
        try:
            intent = payload.get("intent")
            action_plan = payload.get("action_plan") or self._infer_action_plan(intent)
            normalized_actions = self._normalize_actions(action_plan)

            results: List[Dict[str, Any]] = []
            for action in normalized_actions:
                results.append(self._simulate_action(action, payload))

            status = "completed" if all(r.get("status") == "completed" for r in results) else "partial"
            execution_result = {
                "status": status,
                "results": results,
                "executed_at": datetime.now(timezone.utc).isoformat(),
            }

            self.logger.info("Execution completed with status=%s for %d action(s)", status, len(results))
            return {**payload, "execution_result": execution_result, "action_plan": normalized_actions}

        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Execution coordination failed: %s", exc)
            fallback = {
                "status": "error",
                "results": [],
                "error": str(exc),
                "executed_at": datetime.now(timezone.utc).isoformat(),
            }
            return {**payload, "execution_result": fallback}

    def _infer_action_plan(self, intent: Any) -> List[Dict[str, Any]]:
        """Generate a minimal plan when none is provided."""
        if isinstance(intent, dict):
            intent_type = intent.get("intent")
        elif isinstance(intent, str):
            intent_type = intent
        else:
            intent_type = None
        mapping = {
            "refund_request": ["process_refund"],
            "delivery_issue": ["provide_tracking_info"],
            "product_issue": ["add_customer_note"],
            "cancellation_request": ["cancel_order"],
        }
        inferred = mapping.get(intent_type, ["add_customer_note"])
        return [{"action": action, "status": "pending", "detail": "inferred_from_intent"} for action in inferred]

    def _normalize_actions(self, action_plan: List[Any]) -> List[Dict[str, Any]]:
        """Coerce action plan entries into dict form."""
        normalized: List[Dict[str, Any]] = []
        for action in action_plan or []:
            if isinstance(action, dict):
                action_name = action.get("action") or action.get("name")
                if not action_name:
                    continue
                normalized.append(
                    {
                        "action": action_name,
                        "status": action.get("status", "pending"),
                        "detail": action.get("detail", ""),
                        "order_id": action.get("order_id"),
                        "created_at": action.get("created_at", datetime.now(timezone.utc).isoformat()),
                    }
                )
            elif isinstance(action, str):
                normalized.append(
                    {
                        "action": action,
                        "status": "pending",
                        "detail": "inferred_from_string",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
        return normalized

    def _simulate_action(self, action: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return a mock execution result for the given action."""
        action_name = action.get("action", "unknown")
        order = (payload.get("context") or {}).get("order") or {}

        detail = action.get("detail", "")
        if action_name == "process_refund":
            detail = detail or "Issued refund to the original payment method"
        elif action_name == "provide_tracking_info":
            tracking = (payload.get("context") or {}).get("tracking") or {}
            detail = detail or f"Shared tracking status: {tracking.get('status', 'unknown')}"
        elif action_name == "cancel_order":
            detail = detail or "Submitted cancellation request to fulfillment team"
        elif action_name == "add_customer_note":
            detail = detail or "Logged the conversation for follow-up"
        elif action_name == "expedite_delivery":
            detail = detail or "Requested carrier to prioritize the shipment"
        elif action_name == "check_order_status":
            detail = detail or f"Order status: {order.get('status', 'unknown')}"

        return {
            **action,
            "status": "completed",
            "detail": detail,
            "order_id": action.get("order_id") or order.get("order_id"),
        }
