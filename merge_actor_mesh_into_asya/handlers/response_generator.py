"""
Asya-compatible ResponseGenerator in payload mode.

Creates empathetic, template-based replies using the enriched payload. Avoids
LLM calls to keep the demo self contained while still providing structured
responses and an action plan for the ExecutionCoordinator.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


class ResponseGenerator:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        self.intent_templates: Dict[str, str] = {
            "refund_request": "I understand you want a refund for your order{order_clause}. I'll make sure we process that quickly.",
            "delivery_issue": "I can check the latest delivery status{order_clause} and keep you updated.",
            "product_issue": "I'm sorry the product did not meet expectations{order_clause}. I'll help fix this.",
            "billing_issue": "I'll review the billing details and clarify any unexpected charges.",
            "cancellation_request": "I can help cancel the order{order_clause} and confirm once it's done.",
            "account_issue": "I'll help you regain access to your account safely.",
            "escalation_request": "I'll route this to a supervisor so we can address it quickly.",
            "general_inquiry": "I'm here to help and will provide the details you need.",
        }

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a customer-facing response and action plan."""
        try:
            sentiment = payload.get("sentiment") or {}
            intent_raw = payload.get("intent")
            intent = intent_raw if isinstance(intent_raw, dict) else {}
            context = payload.get("context") or {}

            sentiment_label = self._extract_sentiment_label(sentiment)
            urgency = self._extract_urgency(sentiment)
            intent_type = intent.get("intent")
            if not intent_type and isinstance(intent_raw, str):
                intent_type = intent_raw
            intent_type = intent_type or "general_inquiry"

            tone = self._choose_tone(sentiment_label, urgency)
            action_plan = self._build_action_plan(intent_type, context)
            response_text = self._compose_response_text(intent_type, sentiment_label, context, action_plan)

            response_payload: Dict[str, Any] = {
                "text": response_text,
                "tone": tone,
                "intent": intent_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "urgency": urgency,
                    "sentiment": sentiment_label,
                    "action_items": [step.get("action") for step in action_plan if isinstance(step, dict) and step.get("action")],
                },
            }

            self.logger.info("Response generated for intent=%s tone=%s", intent_type, tone)
            return {**payload, "response": response_payload, "action_plan": action_plan}

        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Response generation failed: %s", exc)
            fallback = {
                "text": "Thanks for reaching out. We are looking into this and will follow up shortly.",
                "tone": "professional",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {"error": str(exc)},
            }
            return {**payload, "response": fallback, "action_plan": []}

    def _extract_sentiment_label(self, sentiment: Dict[str, Any]) -> str:
        sentiment_info = sentiment.get("sentiment", sentiment)
        if isinstance(sentiment_info, dict):
            return str(sentiment_info.get("label", "neutral")).lower()
        if isinstance(sentiment_info, str):
            return sentiment_info.lower()
        return "neutral"

    def _extract_urgency(self, sentiment: Dict[str, Any]) -> str:
        urgency = sentiment.get("urgency", {})
        if isinstance(urgency, dict):
            return str(urgency.get("level", "low")).lower()
        if isinstance(urgency, str):
            return urgency.lower()
        return "low"

    def _choose_tone(self, sentiment_label: str, urgency: str) -> str:
        if urgency in {"high", "critical"}:
            return "concise"
        if sentiment_label == "negative":
            return "empathetic"
        if sentiment_label == "positive":
            return "cheerful"
        return "professional"

    def _compose_response_text(
        self,
        intent_type: str,
        sentiment_label: str,
        context: Dict[str, Any],
        action_plan: List[Dict[str, Any]],
    ) -> str:
        """Build a short, empathetic response string."""
        order_clause = ""
        order = context.get("order") or {}
        if order.get("order_id"):
            order_clause = f" for order #{order['order_id']}"

        template = self.intent_templates.get(intent_type, self.intent_templates["general_inquiry"])
        core = template.format(order_clause=order_clause)

        sentiment_prefix = {
            "negative": "I'm sorry you're experiencing this. ",
            "positive": "Thank you for the feedback! ",
            "neutral": "",
        }.get(sentiment_label, "")

        context_bits = self._format_context_details(context)
        next_steps = self._format_next_steps(action_plan)

        return " ".join(part for part in [sentiment_prefix + core, context_bits, next_steps] if part)

    def _format_context_details(self, context: Dict[str, Any]) -> str:
        pieces: List[str] = []
        order = context.get("order") or {}
        tracking = context.get("tracking") or {}

        if order.get("status"):
            pieces.append(f"Current order status: {order['status']}.")
        if tracking.get("status"):
            eta = tracking.get("expected_delivery")
            eta_text = f" ETA: {eta}." if eta else ""
            pieces.append(f"Latest tracking update: {tracking['status']}.{eta_text}")

        return " ".join(pieces)

    def _format_next_steps(self, action_plan: List[Dict[str, Any]]) -> str:
        if not action_plan:
            return ""
        primary_actions = [
            step.get("action", "").replace("_", " ")
            for step in action_plan[:2]
            if isinstance(step, dict) and step.get("action")
        ]
        if not primary_actions:
            return ""
        return f"Next steps: {', '.join(primary_actions)}."

    def _build_action_plan(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a short list of actions for ExecutionCoordinator."""
        order_id = (context.get("order") or {}).get("order_id")

        def step(action: str, detail: str) -> Dict[str, Any]:
            return {
                "action": action,
                "status": "pending",
                "detail": detail,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "order_id": order_id,
            }

        if intent_type == "refund_request":
            return [
                step("check_order_status", "Confirm order eligibility for refund"),
                step("process_refund", "Initiate refund to original payment method"),
            ]
        if intent_type == "delivery_issue":
            return [
                step("provide_tracking_info", "Share the most recent tracking event"),
                step("expedite_delivery", "Request carrier to prioritize shipment"),
            ]
        if intent_type == "product_issue":
            return [
                step("add_customer_note", "Log product issue for follow-up"),
                step("generate_return_label", "Provide return instructions if needed"),
            ]
        if intent_type == "cancellation_request":
            return [step("cancel_order", "Attempt to cancel before fulfillment completes")]
        if intent_type == "billing_issue":
            return [step("add_customer_note", "Document billing concern for finance review")]
        if intent_type == "account_issue":
            return [step("schedule_callback", "Arrange a secure callback to verify identity")]
        if intent_type == "escalation_request":
            return [step("escalate_to_supervisor", "Route to human supervisor for review")]

        return [step("add_customer_note", "Record the inquiry and keep the customer updated")]
