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

Detailed implementation steps

1) Spin up Asya kind stack (SQS profile matches the boss note):  
   - `cd asya`  
   - `PROFILE=sqs-s3 make up-e2e` (cluster name `asya-e2e-sqs-s3`).  
   - Export `KUBECONFIG=$(pwd)/testing/e2e/.kube/config` if kubectl cannot see the cluster.
2) Wire the route/envelope you send for testing:  
   - Envelope shape to post to SQS (LocalStack endpoint from the e2e profile):  
     ```json
     {
       "id": "demo-1",
       "route": {"actors": ["decision-router", "response-generator", "response-aggregator"], "current": 0},
       "payload": {
         "customer_message": "My order arrived damaged",
         "customer_email": "vip@example.com",
         "sentiment": {"urgency": "high", "sentiment": "negative", "intensity": 0.9},
         "intent": {"intent": "refund_request", "confidence": 0.92},
         "context": {"customer": {"tier": "VIP"}, "orders": [1, 2, 3]}
       }
     }
     ```
   - Send:  
     `aws --endpoint-url http://localhost:4566 sqs send-message --queue-url http://localhost:4566/000000000000/asya-decision-router --message-body '...json above...'`
   - Check logs: `kubectl logs -l asya.sh/actor=decision-router -c asya-runtime -n asya-e2e`.
3) Validate end-to-end:  
   - Use `kubectl get asya -n asya-e2e` to confirm CR status.  
   - For multi-actor chains, ensure `route["current"]` increments and queues exist (`kubectl get queues` via operator CRDs or check LocalStack SQS).  
   - Add minimal pytest-style smoke tests that call handlers directly in Python to assert route edits before containerizing.
4) Iterate:  
   - Once DecisionRouter works, port the next actor by reusing the same image (add module, rebuild, `kind load ...`, `kubectl rollout restart deployment/<actor>`).  
   - When all actors exist, craft a single envelope with the full pipeline (`["sentiment-analyzer", "intent-analyzer", "context-retriever", "decision-router", "response-generator", "guardrail-validator", "execution-coordinator", "response-aggregator"]`) and verify the flow.

Debugging note

- Pod label selector: the operator labels pods with `asya.sh/asya=<actor>` (and `app=<actor>`). Use `kubectl get pods -n asya-e2e -l asya.sh/asya=decision-router` to find the pod; `asya.sh/actor` will return nothing.
- LocalStack CLI reminder: set dummy AWS creds and region when using `aws` against LocalStack, then send the test envelope:
  ```bash
  export AWS_ACCESS_KEY_ID=test
  export AWS_SECRET_ACCESS_KEY=test
  aws --region us-east-1 --endpoint-url http://localhost:4566 sqs send-message \
    --queue-url http://localhost:4566/000000000000/asya-decision-router \
    --message-body '{
      "id": "demo-1",
      "route": {"actors": ["decision-router","response-generator","response-aggregator"], "current": 0},
      "payload": {
        "customer_message": "My VIP order is damaged and I need a refund ASAP!",
        "customer_email": "vip@example.com",
        "sentiment": {"urgency": "high", "sentiment": "negative", "intensity": 0.9},
      "intent": {"intent": "refund_request", "confidence": 0.92},
        "context": {"customer": {"tier": "VIP"}, "orders": [1, 2, 3]}
      }
    }'
  ```
- Next actor test (sentiment → decision-router chain):
  - Apply: `kubectl apply -f tinkering_with_asya/merge_actor_mesh_into_asya/sentiment-analyzer.yaml`
  - Port-forward SQS if needed: `kubectl port-forward -n asya-e2e svc/localstack-sqs 4566:4566`
  - Send a message to the first actor in the route:
    ```bash
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    aws --region us-east-1 --endpoint-url http://localhost:4566 sqs send-message \
      --queue-url http://localhost:4566/000000000000/asya-sentiment-analyzer \
      --message-body '{
        "id": "demo-2",
        "route": {"actors": ["sentiment-analyzer","decision-router","response-generator","response-aggregator"], "current": 0},
        "payload": {
          "customer_message": "Where is my order, it is one day late?",
          "customer_email": "user@example.com"
      }
    }'
    ```
  - Tail logs: `kubectl logs -n asya-e2e -l asya.sh/asya=sentiment-analyzer -c asya-runtime -f` and then `decision-router` to confirm the route continues normally.
- Escalation path check: send a high-urgency/VIP envelope to confirm DecisionRouter logs “Immediate escalation...”:
  ```bash
  aws --region us-east-1 --endpoint-url http://localhost:4566 sqs send-message \
    --queue-url http://localhost:4566/000000000000/asya-sentiment-analyzer \
    --message-body '{
      "id": "demo-escalate",
      "route": {"actors": ["sentiment-analyzer","decision-router","response-generator","response-aggregator"], "current": 0},
      "payload": {
        "customer_message": "I am furious, this is unacceptable. Fix it now!",
        "customer_email": "vip@example.com",
        "sentiment": {"urgency": "critical", "sentiment": "negative", "intensity": 0.95},
        "intent": {"intent": "refund_request", "confidence": 0.4},
        "context": {"customer": {"tier": "VIP"}, "orders": [1,2,3]}
      }
    }'
  ```
  Tail `decision-router` logs to see the escalation routing message.


Key translation hints per actor

- Sentiment/Intent/Context: payload mode, return `{**payload, "sentiment": ..., "intent": ...}`. No manual routing changes; Asya will advance to the next actor.
- ResponseGenerator/GuardrailValidator/ExecutionCoordinator: payload mode; preserve existing fields and append new keys. Raise exceptions for failures to leverage `asya-error-end`.
- ResponseAggregator: payload mode; can terminate early by returning `None` to skip happy-end or pass through final payload to crew.
- EscalationRouter: envelope mode; similar to DecisionRouter but likely rewrites the future route to human handoff and adds `payload["recovery_log"]` entries.
