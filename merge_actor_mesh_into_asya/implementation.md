Integration notes on merging Actor Mesh business logic into Asya

- Envelope vs Message: Asya actors receive a plain dict envelope: `{"id": "...", "payload": {...}, "route": {"actors": [...], "current": 0}, "headers": {...}}`. Replace the `Message/Route` pydantic objects with direct dict access (`payload = env["payload"]`, `route = env["route"]`). Map `route.steps` → `route["actors"]`, `route.current_step` → `route["current"]`, and carry any `error_handler` into `headers` or a `payload["error_handler"]` field you read yourself.
- Routing semantics: In envelope mode Asya increments `route["current"]` only if you return a payload; routers that change the route must keep the already-processed actors intact (`route["actors"][:route["current"]+1]`). Add or replace only the future steps. To jump to a new path (e.g., immediate escalation), rebuild the tail: `route["actors"] = route["actors"][:route["current"]+1] + ["escalation-router", "response-aggregator"]; route["current"] += 1`.
- Transport shift: Actor Mesh publishes to NATS; Asya sidecars read from queues named `asya-<actor>`. Remove `send_message` calls; simply mutate and return the envelope. Fan-out remains supported by returning a list. Raising an exception routes to `asya-error-end`, so only keep bespoke error routing if the business rules demand it.
- Payload fidelity: Keep the original payload shape (`customer_message`, `customer_email`, enrichments) so later actors can be ported with minimal changes. Any metadata (timestamps/retry counts) can live under `headers` or a `payload["metadata"]` map.
- Mode selection: Routers (DecisionRouter/EscalationRouter) must run with `ASYA_HANDLER_MODE=envelope` to see and edit routes. Processing actors (sentiment/intent/context/response/guardrail/execution/aggregator) can stay in default payload mode.
- Scaling/observability: Asya handles autoscaling via KEDA and queue depth. You get logs per pod plus sidecar metrics (`asya_actor_envelopes_total`, `asya_actor_processing_seconds`). No need to port custom retry loops; rely on queue redrive and Kubernetes restart policies unless a rule truly needs application-level retries.

Proposed migration plan (actor order)

1) DecisionRouter (unblocks end-to-end flow).  
2) SentimentAnalyzer and IntentAnalyzer (payload mode).  
3) ContextRetriever (payload mode, wire to mock services).  
4) ResponseGenerator and GuardrailValidator.  
5) ExecutionCoordinator and ResponseAggregator.  
6) EscalationRouter (optional once basic path works).


Key translation hints per actor

- Sentiment/Intent/Context: payload mode, return `{**payload, "sentiment": ..., "intent": ...}`. No manual routing changes; Asya will advance to the next actor.
- ResponseGenerator/GuardrailValidator/ExecutionCoordinator: payload mode; preserve existing fields and append new keys. Raise exceptions for failures to leverage `asya-error-end`.
- ResponseAggregator: payload mode; can terminate early by returning `None` to skip happy-end or pass through final payload to crew.
- EscalationRouter: envelope mode; similar to DecisionRouter but likely rewrites the future route to human handoff and adds `payload["recovery_log"]` entries.
