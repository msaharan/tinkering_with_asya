# Comparison: actor-mesh-demo vs merge_actor_mesh_into_asya

## Overview
- **actor-mesh-demo**: Full reference with NATS JetStream, Pydantic Message/Route models, LLM-backed intent/response, HTTP mock services, Redis/SQLite, API gateway, and web widget.
- **merge_actor_mesh_into_asya**: Asya/SQS port of the ecommerce logic. Uses the Asya Flow DSL entrypoint to stitch the pipeline, payload-mode handlers with envelope-mode routers kept for manual routing, offline rule-based logic, and in-memory mocks only (no gateway/widget or external deps).

## Orchestration and transport
- **actor-mesh-demo**: NATS subjects `ecommerce.support.*`, Message/Route helpers, HTTP/WebSocket gateway bridging UI to NATS.
- **Asya port**: AsyncActor CRs on SQS queues (`asya-<namespace>-<actor>`). Flow entrypoint `start-ecommerce-flow` (compiled from `flows/ecommerce_flow.py` to `build/ecommerce_flow_compiled/routers.py`) injects the fixed processing chain and advances `route["current"]`. DecisionRouter/EscalationRouter run envelope mode for dynamic/manual routing; other actors run payload mode and rely on the sidecar to advance routing.

## Actor behavior
- **SentimentAnalyzer**: Rule-based lexicons with negation/intensifier handling; returns sentiment/urgency/complaint/escalation flags plus keyword audit and timestamps.
- **IntentAnalyzer**: Keyword/regex heuristics; extracts entities (order number, tracking id, email) with heuristic confidence.
- **ContextRetriever**: Looks up mock customer/order/tracking records from in-memory dicts, guards against customer/order mismatch, notes missing context.
- **ResponseGenerator**: Template/tone selection driven by sentiment+urgency; builds an order-aware action_plan for ExecutionCoordinator and contextualizes with order/tracking snippets.
- **GuardrailValidator**: Regex checks for risky promises/PII and length; emits `guardrail_check` with issues and recommended action.
- **ExecutionCoordinator**: Normalizes or infers action_plan, simulates completion details using context, returns `execution_result`.
- **DecisionRouter**: Envelope-mode route mutations—immediate escalation on critical urgency/strong negative/VIP+urgent/legal, priority routing, injects ExecutionCoordinator for actionable intents, adds human review on low confidence, re-inserts ContextRetriever for complex queries, and manually advances `route["current"]`.
- **EscalationRouter**: Marks payload escalated with reasons (guardrail failure, intent confidence <0.6, negative sentiment, etc.), appends `recovery_log`, and rewrites the remaining route to finish at ResponseAggregator.
- **ResponseAggregator**: Assembles `final_response` with status `resolved`/`needs_review`/`escalated`, carries guardrail/execution metadata, but does not deliver externally.

## State and storage
- **actor-mesh-demo**: Redis cache + SQLite history/audit with mock HTTP services.
- **Asya port**: No Redis/SQLite or HTTP calls; all state lives in the payload/envelope during a single run.

## Entry/exit points
- **actor-mesh-demo**: FastAPI gateway and web widget deliver customer chat.
- **Asya port**: Entry via SQS message to `start-ecommerce-flow` (or individual actor queues); output is the enriched payload/final_response on the queue—no HTTP gateway or UI.

## Deployment/build
- **actor-mesh-demo**: k3d manifests for NATS/Redis/SQLite plus API/web assets; LLM paths enabled.
- **Asya port**: AsyncActor manifests per handler plus Flow start actor; two images (`actor-mesh-asya:dev` handlers, `ecommerce-flow-routers:dev` compiled runtime via `Makefile flow-*`); targets the Asya kind stack with LocalStack SQS; no NATS/Redis/SQLite sidecars.

## Robustness summary
- **actor-mesh-demo** remains the full-featured reference (LLM paths, persistence, gateway, retries, monitoring).
- **merge_actor_mesh_into_asya** is deterministic/offline for local Asya SQS choreography (simple routing, simulated actions, no persistence or external integrations).
