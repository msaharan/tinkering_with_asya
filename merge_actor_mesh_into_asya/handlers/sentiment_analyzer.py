"""
Asya-compatible SentimentAnalyzer in payload mode.

Ports the rule-based sentiment/urgency/complaint analysis from Actor Mesh to
operate on plain dict payloads. Returns the original payload with a new
`sentiment` key containing analysis results.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Set


class SentimentAnalyzer:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger("asya.sentiment-analyzer")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level.upper())

        # Lexicons
        self.positive_words: Set[str] = {
            "good", "great", "excellent", "amazing", "awesome", "fantastic",
            "wonderful", "perfect", "love", "like", "happy", "pleased",
            "satisfied", "delighted", "thrilled", "glad", "appreciate",
            "thank", "thanks", "grateful", "helpful", "smooth", "easy",
            "fast", "quick", "efficient", "professional", "friendly",
            "polite", "courteous", "reliable", "trustworthy", "quality",
            "value", "recommend", "impressed", "outstanding", "superb",
            "brilliant", "marvelous", "terrific", "splendid", "nice",
        }

        self.negative_words: Set[str] = {
            "bad", "terrible", "horrible", "awful", "worst", "hate", "angry",
            "frustrated", "annoyed", "disappointed", "upset", "mad", "furious",
            "disgusted", "outraged", "appalled", "shocked", "disturbed",
            "concerned", "worried", "confused", "lost", "stuck", "broken",
            "failed", "error", "problem", "issue", "trouble", "difficulty",
            "slow", "delayed", "late", "wrong", "incorrect", "useless",
            "worthless", "waste", "money", "time", "poor", "cheap", "fake",
            "scam", "fraud", "lies", "lying", "dishonest", "rude", "unprofessional",
        }

        self.urgency_words: Set[str] = {
            "urgent", "emergency", "asap", "immediately", "now", "today",
            "critical", "important", "rush", "quick", "fast", "soon",
            "deadline", "time-sensitive", "expire", "expires", "expired",
            "last", "final", "closing", "ending", "limited", "running out",
            "yesterday", "overdue", "late", "delayed", "missing",
        }

        self.complaint_words: Set[str] = {
            "complaint", "complain", "problem", "issue", "wrong", "error",
            "mistake", "broken", "defective", "damaged", "missing", "lost",
            "delayed", "late", "slow", "cancel", "refund", "return",
            "exchange", "replacement", "fix", "repair", "resolve", "solution",
            "manager", "supervisor", "order", "upset", "frustrated", "annoyed",
            "disappointed", "angry", "furious", "unacceptable", "terrible",
            "awful", "horrible",
        }

        self.escalation_words: Set[str] = {
            "manager", "supervisor", "escalate", "lawyer", "legal", "sue",
            "court", "attorney", "corporate", "headquarters", "ceo", "president",
            "director", "complaint", "report", "review", "rating", "terrible",
            "worst", "never", "again", "boycott", "social", "media", "twitter",
            "facebook", "instagram", "news", "press", "public",
        }

        self.intensifiers: Set[str] = {
            "very", "extremely", "really", "quite", "totally", "completely",
            "absolutely", "definitely", "certainly", "incredibly", "amazingly",
            "exceptionally", "remarkably", "particularly", "especially",
            "highly", "deeply", "truly", "genuinely", "seriously",
        }

        self.negation_words: Set[str] = {
            "not", "no", "never", "nothing", "nobody", "nowhere", "neither",
            "nor", "none", "hardly", "scarcely", "barely", "seldom", "rarely",
            "without", "lack", "lacks", "lacking", "missing", "absent",
            "doesn't", "don't", "won't", "can't", "couldn't", "shouldn't",
            "wouldn't", "isn't", "aren't", "wasn't", "weren't", "haven't",
            "hasn't", "hadn't",
        }

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment/urgency and return the enriched payload."""
        try:
            customer_email = payload.get("customer_email", "unknown")
            self.logger.info("Processing sentiment for %s", customer_email)

            content = str(payload.get("customer_message") or "").lower()

            sentiment_result = self._analyze_sentiment(content)
            urgency_result = self._analyze_urgency(content)
            complaint_result = self._analyze_complaint(content)
            escalation_result = self._analyze_escalation(content)

            analysis_result: Dict[str, Any] = {
                "sentiment": sentiment_result,
                "urgency": urgency_result,
                "is_complaint": complaint_result["is_complaint"],
                "escalation_needed": escalation_result["escalation_needed"],
                "keywords_detected": {
                    "sentiment_keywords": sentiment_result.get("keywords", []),
                    "urgency_keywords": urgency_result.get("keywords", []),
                    "complaint_keywords": complaint_result.get("keywords", []),
                    "escalation_keywords": escalation_result.get("keywords", []),
                },
                "analysis_method": "rule_based",
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "model_info": {
                    "analyzer_type": "rule_based",
                    "version": "1.0.0",
                    "compatible_with": "all_platforms",
                },
            }

            self.logger.info(
                "Sentiment completed: %s (confidence %.2f, urgency %s)",
                sentiment_result.get("label", "neutral"),
                float(sentiment_result.get("confidence", 0.0)),
                urgency_result.get("level", "low"),
            )

            # Store under payload["sentiment"] to match DecisionRouter expectations.
            return {**payload, "sentiment": analysis_result}

        except Exception as exc:  # pragma: no cover - safety net
            self.logger.error("Sentiment analysis error: %s", exc)
            fallback = {
                "sentiment": {"label": "neutral", "confidence": 0.0},
                "urgency": {"level": "low", "score": 0.0},
                "is_complaint": False,
                "escalation_needed": False,
                "analysis_method": "error_fallback",
                "error": str(exc),
            }
            return {**payload, "sentiment": fallback}

    # --- Analysis helpers ---
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\\b\\w+\\b", text.lower())
        positive_score = 0.0
        negative_score = 0.0
        found_keywords: List[str] = []

        for i, word in enumerate(words):
            negated = any(neg in words[max(0, i - 2) : i] for neg in self.negation_words)
            intensified = any(intens in words[max(0, i - 2) : i] for intens in self.intensifiers)
            multiplier = 1.5 if intensified else 1.0

            if word in self.positive_words:
                score = multiplier
                if negated:
                    negative_score += score
                else:
                    positive_score += score
                found_keywords.append(word)
            elif word in self.negative_words:
                score = multiplier
                if negated:
                    positive_score += score
                else:
                    negative_score += score
                found_keywords.append(word)

        total_score = positive_score - negative_score
        total_words = len([w for w in words if w in self.positive_words or w in self.negative_words])

        if total_words == 0:
            return {"label": "neutral", "confidence": 0.0, "score": 0.0, "keywords": found_keywords}

        confidence = min(abs(total_score) / max(total_words, 1), 1.0)

        if total_score > 0.5:
            label = "positive"
        elif total_score < -0.5:
            label = "negative"
        else:
            label = "neutral"

        return {"label": label, "confidence": confidence, "score": total_score, "keywords": found_keywords}

    def _analyze_urgency(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\\b\\w+\\b", text.lower())
        urgency_score = 0
        found_keywords: List[str] = []

        for word in words:
            if word in self.urgency_words:
                urgency_score += 1
                found_keywords.append(word)

        urgency_patterns = [
            r"\\b(today|tonight|this\\s+week)\\b",
            r"\\b(expires?|expire)\\s+(today|tomorrow|soon)\\b",
            r"\\b(need|want|require).{0,20}(immediately|asap|urgently)\\b",
            r"\\b(time\\s+sensitive|time-sensitive)\\b",
            r"\\b(deadline|due\\s+date)\\b",
            r"\\b(supposed\\s+to\\s+(arrive|come|be\\s+here))\\s+(yesterday|today)\\b",
            r"\\b(should\\s+have\\s+(arrived|come|been\\s+here))\\b",
            r"\\b(was\\s+(supposed|expected))\\s+to\\b",
        ]

        for pattern in urgency_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                urgency_score += 2

        if urgency_score >= 3:
            level = "high"
        elif urgency_score >= 1:
            level = "medium"
        else:
            level = "low"

        return {"level": level, "score": urgency_score, "keywords": found_keywords}

    def _analyze_complaint(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\\b\\w+\\b", text.lower())
        complaint_score = 0
        found_keywords: List[str] = []

        complaint_patterns = [
            r"\\b(i\\s+want\\s+to\\s+complain|file\\s+a\\s+complaint)\\b",
            r"\\b(this\\s+is\\s+(terrible|awful|horrible))\\b",
            r"\\b(not\\s+satisfied|unsatisfied|disappointed)\\b",
            r"\\b(want\\s+(refund|money\\s+back|return))\\b",
            r"\\b(something\\s+is\\s+wrong|there\\s+is\\s+a\\s+problem)\\b",
            r"\\b(very\\s+(frustrated|angry|upset))\\b",
        ]

        for pattern in complaint_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                complaint_score += 3

        positive_context_patterns = [
            r"\\b(thank\\s+you|thanks|grateful|appreciate)\\b",
            r"\\b(excellent|wonderful|great|amazing|fantastic)\\b",
            r"\\b(happy|pleased|satisfied|love)\\b",
        ]

        has_strong_positive_context = any(re.search(pattern, text, re.IGNORECASE) for pattern in positive_context_patterns)

        for word in words:
            if word in self.complaint_words:
                complaint_score += 1
                found_keywords.append(word)

        threshold = 4 if has_strong_positive_context else 2
        is_complaint = complaint_score >= threshold

        return {"is_complaint": is_complaint, "score": complaint_score, "keywords": found_keywords}

    def _analyze_escalation(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\\b\\w+\\b", text.lower())
        escalation_score = 0
        found_keywords: List[str] = []

        for word in words:
            if word in self.escalation_words:
                escalation_score += 1
                found_keywords.append(word)

        escalation_patterns = [
            r"\\b(speak\\s+to\\s+(your\\s+)?(manager|supervisor))\\b",
            r"\\b(this\\s+is\\s+unacceptable)\\b",
            r"\\b(i\\s+will\\s+(sue|report|review))\\b",
            r"\\b(terrible\\s+service|worst\\s+experience)\\b",
        ]

        for pattern in escalation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                escalation_score += 3

        escalation_needed = escalation_score >= 3
        return {"escalation_needed": escalation_needed, "score": escalation_score, "keywords": found_keywords}
