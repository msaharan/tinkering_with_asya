# Comparison: actor-mesh-demo vs merge_actor_mesh_into_asya

## Overview
- **actor-mesh-demo**: Full reference implementation with NATS JetStream, Pydantic Message/Route models, LLM-based intent/response, HTTP mock services, Redis/SQLite storage, API gateway, and web widget. Deploys to k3d with NATS/Redis/SQLite.
- **merge_actor_mesh_into_asya**: Ported to Asya/SQS. Uses envelope dicts, lightweight rule-based logic, in-memory mocks, no external services or storage, and only actor manifests (no API gateway/widget).

## Transport and protocol
- **actor-mesh-demo**: NATS subjects `ecommerce.support.*`, Message/Route classes with serialization and route helpers.
- **Asya port**: SQS queues `asya-<actor>`, raw envelope dicts (`route["actors"]`/`route["current"]`), no Message/Route classes.

## Actor behavior
- **SentimentAnalyzer**: Demo offers rule-based + ML variant; Asya port keeps rule-based only.
- **IntentAnalyzer**: Demo uses LLM prompt + JSON parsing; Asya port is keyword/regex heuristic with fixed confidence.
- **ContextRetriever**: Demo hits mock HTTP services and caches in Redis; Asya port uses in-memory dicts, no HTTP or caching.
- **ResponseGenerator**: Demo uses LLM prompt with context; Asya port uses deterministic templates, no LLM.
- **GuardrailValidator**: Demo combines regex and optional LLM, logs to SQLite; Asya port is light regex only, no SQLite audit.
- **ExecutionCoordinator**: Demo calls mock APIs; Asya port simulates action results in-memory.
- **DecisionRouter**: Demo modifies Message.Route; Asya port mutates envelope route and now advances `route["current"]` explicitly.
- **EscalationRouter**: Demo handles retries/human handoff; Asya port rewrites route to aggregator and logs reasons.
- **ResponseAggregator**: Demo logs to SQLite and delivers to gateway; Asya port just appends `final_response`, no SQLite or gateway.

## Storage and state
- **actor-mesh-demo**: Redis for session/context cache; SQLite for conversation history/audit.
- **Asya port**: No Redis/SQLite integration; all state is transient in payload/envelope.

## Entry/exit points
- **actor-mesh-demo**: FastAPI API gateway and web widget included.
- **Asya port**: No gateway/widget; interaction via SQS messages only.

## Deployment
- **actor-mesh-demo**: k3d manifests for NATS/Redis/SQLite and actors.
- **Asya port**: AsyncActor CRs for SQS transport; no NATS/Redis/SQLite manifests; Docker image is minimal Python 3.12 with handlers only.

## Robustness summary
- **actor-mesh-demo** remains the more complete/production-like implementation (external services, storage, LLM paths, gateway, persistence).
- **merge_actor_mesh_into_asya** is intentionally lightweight for Asya/SQS choreography demos (self-contained, no external deps, deterministic logic), but lacks the richer behaviors and persistence of the demo.
