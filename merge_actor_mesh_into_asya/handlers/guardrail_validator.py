"""
Asya-compatible GuardrailValidator in payload mode.

Performs lightweight rule-based validation on generated responses to catch
unauthorized promises, risky phrasing, or missing content. Appends a
``guardrail_check`` field to the payload with the outcome.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


class GuardrailValidator:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        self.unauthorized_promises = [
            r"guarantee",
            r"will\s+definitely",
            r"promise\s+you",
            r"for\s+sure",
            r"100%\s+refun",
        ]
        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN style
            r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b",  # spaced CC
            r"\b\d{15,16}\b",  # numeric CC
        ]

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated response and append guardrail results."""
        try:
            response_text = self._extract_response_text(payload.get("response"))
            if not response_text:
                result = {
                    "pass": False,
                    "issues": [{"type": "missing_response", "message": "No response text to validate"}],
                    "validated_at": datetime.now(timezone.utc).isoformat(),
                }
                return {**payload, "guardrail_check": result}

            issues: List[Dict[str, Any]] = []
            issues.extend(self._check_patterns(response_text, self.unauthorized_promises, "unauthorized_promise"))
            issues.extend(self._check_patterns(response_text, self.pii_patterns, "pii_risk"))

            if len(response_text) > 2000:
                issues.append({"type": "length", "message": "Response too long", "severity": "low"})

            passed = len(issues) == 0
            result = {
                "pass": passed,
                "issues": issues,
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "recommended_action": "regenerate" if not passed else "deliver",
            }

            if not passed:
                self.logger.warning("Guardrail validation failed with %d issue(s)", len(issues))
            else:
                self.logger.info("Guardrail validation passed")

            return {**payload, "guardrail_check": result}

        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Guardrail validation error: %s", exc)
            fallback = {
                "pass": False,
                "issues": [{"type": "error", "message": str(exc), "severity": "high"}],
                "validated_at": datetime.now(timezone.utc).isoformat(),
            }
            return {**payload, "guardrail_check": fallback}

    def _extract_response_text(self, response: Any) -> str:
        if isinstance(response, dict):
            return str(response.get("text") or response.get("response_text") or "")
        if response is None:
            return ""
        return str(response)

    def _check_patterns(self, text: str, patterns: List[str], issue_type: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({"type": issue_type, "pattern": pattern, "severity": "high"})
        return issues
