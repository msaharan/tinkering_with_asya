"""Example Flow DSL definition that stitches the existing ecommerce handlers."""

import handlers.context_retriever
import handlers.execution_coordinator
import handlers.guardrail_validator
import handlers.intent_analyzer
import handlers.response_aggregator
import handlers.response_generator
import handlers.sentiment_analyzer


def ecommerce_flow(p: dict) -> dict:
    sentiment = handlers.sentiment_analyzer.SentimentAnalyzer()
    intent = handlers.intent_analyzer.IntentAnalyzer()
    context = handlers.context_retriever.ContextRetriever()
    responder = handlers.response_generator.ResponseGenerator()
    guardrail = handlers.guardrail_validator.GuardrailValidator()
    executor = handlers.execution_coordinator.ExecutionCoordinator()
    aggregator = handlers.response_aggregator.ResponseAggregator()

    p = sentiment.process(p)
    p = intent.process(p)
    p = context.process(p)
    p = responder.process(p)
    p = guardrail.process(p)
    p = executor.process(p)
    p = aggregator.process(p)
    return p
