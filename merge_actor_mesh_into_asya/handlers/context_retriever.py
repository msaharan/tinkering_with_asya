"""
Asya-compatible ContextRetriever in payload mode.

Simulates the Actor Mesh context enrichment step with local in-memory data.
Fetches customer, order, and tracking details (when available) and appends a
``context`` object to the payload for downstream actors.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)


class ContextRetriever:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Mock data representing our "APIs"
        self.customers: Dict[str, Dict[str, Any]] = {
            "user@example.com": {
                "id": "cust_001",
                "name": "John Doe",
                "tier": "premium",
                "email": "user@example.com",
            },
            "vip@example.com": {
                "id": "cust_002",
                "name": "Casey VIP",
                "tier": "VIP",
                "email": "vip@example.com",
            },
        }

        self.orders: Dict[str, Dict[str, Any]] = {
            "12345": {
                "order_id": "12345",
                "customer_id": "cust_001",
                "items": ["Wireless Headphones"],
                "status": "shipped",
                "tracking_id": "1Z999AA10123456784",
                "expected_delivery": "2025-10-02",
            },
            "98765": {
                "order_id": "98765",
                "customer_id": "cust_002",
                "items": ["Coffee Machine"],
                "status": "processing",
                "tracking_id": None,
                "expected_delivery": "2025-10-05",
            },
        }

        self.tracking: Dict[str, Dict[str, Any]] = {
            "1Z999AA10123456784": {
                "status": "in_transit",
                "location": "Distribution Center",
                "expected_delivery": "2025-10-02",
            }
        }

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Attach mock context data to the payload."""
        try:
            customer_email = str(payload.get("customer_email") or "").lower()
            intent = payload.get("intent") or {}

            customer_data = self._get_customer(customer_email)
            order_number = self._extract_order_number(intent, payload)
            order_data = self._get_order(order_number, customer_data)
            orders_for_customer = self._get_orders_for_customer(customer_data)
            tracking_data = self._get_tracking(order_data)

            context: Dict[str, Any] = {
                "customer": customer_data,
                "order": order_data,
                "orders": orders_for_customer,
                "tracking": tracking_data,
                "source": "mock_data",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }

            missing: List[str] = []
            if not customer_data:
                missing.append("customer")
            if order_number and not order_data:
                missing.append("order")
            if order_data and order_data.get("tracking_id") and not tracking_data:
                missing.append("tracking")
            if missing:
                context["missing"] = missing

            self.logger.info(
                "Context retrieved: customer=%s order=%s tracking=%s",
                customer_data.get("id") if customer_data else "unknown",
                order_data.get("order_id") if order_data else "none",
                tracking_data.get("status") if tracking_data else "none",
            )

            return {**payload, "context": context}

        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Context retrieval failed: %s", exc)
            fallback = {
                "source": "error",
                "error": str(exc),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
            return {**payload, "context": fallback}

    def _get_customer(self, email: str) -> Dict[str, Any]:
        """Return customer record or a minimal stub."""
        if not email:
            return {}
        return self.customers.get(email, {"id": None, "email": email, "tier": "unknown"})

    def _extract_order_number(self, intent: Any, payload: Dict[str, Any]) -> Optional[str]:
        """Look for an order number in intent entities or raw text."""
        if isinstance(intent, dict):
            entities = intent.get("entities") or {}
            if isinstance(entities, dict):
                order_number = entities.get("order_number") or entities.get("order_id")
                if order_number:
                    return str(order_number)

        message = str(payload.get("customer_message") or "")
        match = re.search(r"\b(\d{5,})\b", message)
        return match.group(1) if match else None

    def _get_order(self, order_number: Optional[str], customer: Dict[str, Any]) -> Dict[str, Any]:
        """Return the order matching the number and customer if known."""
        if not order_number:
            return {}
        order = self.orders.get(order_number, {})
        if order and customer and customer.get("id") and order.get("customer_id") != customer["id"]:
            # Mismatch: avoid leaking other customers' data
            return {}
        return order

    def _get_orders_for_customer(self, customer: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return a small list of recent orders for the customer."""
        if not customer or not customer.get("id"):
            return []
        return [order for order in self.orders.values() if order.get("customer_id") == customer["id"]]

    def _get_tracking(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Return tracking details for the provided order."""
        if not order:
            return {}
        tracking_id = order.get("tracking_id")
        return self.tracking.get(tracking_id, {}) if tracking_id else {}
