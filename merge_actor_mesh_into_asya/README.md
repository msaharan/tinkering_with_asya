# README

This project is being developed as part of the [Asya](https://github.com/deliveryhero/asya) project with the aim of developing a fully functional example exhibiting Asya's use-case through a real-world scenario.

We will take the business logic from [Actor Mesh Demo](https://github.com/msaharan/actor-mesh-demo) and integrate it into Asya such that the entire system is deployed on a local kind cluster.

## Directory structure

```
merge_actor_mesh_into_asya/
├── Dockerfile                     # Handler image for the ported Actor Mesh actors
├── Dockerfile.ecommerce-runtime   # Runtime image for the compiled Flow routers
├── Makefile                       # Flow compile/build/load/restart helpers
├── build/                         # Generated routers, runtime shim, and diagrams
│   └── ecommerce_flow_compiled/
│       ├── routers.py             # Flow DSL compiled into router functions
│       ├── flow.dot / flow.png    # Flow visualization
│       └── Dockerfile             # Build context for the routers image
├── deploy/
│   └── manifests/                 # AsyncActor definitions
│       ├── start-ecommerce-flow.yaml  # Flow entrypoint (SQS → routers image)
│       ├── context-retriever.yaml
│       ├── decision-router.yaml
│       ├── escalation-router.yaml
│       ├── execution-coordinator.yaml
│       ├── guardrail-validator.yaml
│       ├── intent-analyzer.yaml
│       ├── response-aggregator.yaml
│       ├── response-generator.yaml
│       └── sentiment-analyzer.yaml
├── docs/                          # Implementation notes and run steps
│   ├── RUN.md                     # End-to-end setup/run/teardown commands
│   ├── comparison_actormeshdemo_with_asya_implementation.md
│   └── implementation.md
├── flows/
│   └── ecommerce_flow.py          # Flow DSL that wires the handlers together
├── handlers/                      # Ported Actor Mesh handler logic
│   ├── context_retriever.py
│   ├── decision_router.py
│   ├── escalation_router.py
│   ├── execution_coordinator.py
│   ├── guardrail_validator.py
│   ├── intent_analyzer.py
│   ├── response_aggregator.py
│   ├── response_generator.py
│   └── sentiment_analyzer.py
├── selected_logs/                 # Representative logs from a local Asya deployment
└── README.md
```
