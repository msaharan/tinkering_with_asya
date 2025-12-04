# README

This project is being developed as part of the [Asya](https://github.com/deliveryhero/asya) project with the aim of developing a fully functional example exhibiting Asya's use-case through a real-world scenario.

We will take the business logic from [Actor Mesh Demo](https://github.com/msaharan/actor-mesh-demo) and integrate it into Asya such that the entire system is deployed on a local kind cluster.

## Directory Structure

```
merge_actor_mesh_into_asya/
├── Dockerfile                  # Builds the handler image for the Asya actors
├── deploy/
│   └── manifests/              # AsyncActor definitions for each stage in the pipeline
│       ├── context-retriever.yaml
│       ├── decision-router.yaml
│       ├── escalation-router.yaml
│       ├── execution-coordinator.yaml
│       ├── guardrail-validator.yaml
│       ├── intent-analyzer.yaml
│       ├── response-aggregator.yaml
│       ├── response-generator.yaml
│       └── sentiment-analyzer.yaml
├── docs/                       # Implementation notes and run instructions
│   ├── RUN.md
│   ├── comparison_actormeshdemo_with_asya_implementation.md
│   └── implementation.md
├── handlers/                   # Ported handler logic for each actor
│   ├── context_retriever.py
│   ├── decision_router.py
│   ├── escalation_router.py
│   ├── execution_coordinator.py
│   ├── guardrail_validator.py
│   ├── intent_analyzer.py
│   ├── response_aggregator.py
│   ├── response_generator.py
│   └── sentiment_analyzer.py
├── selected_logs/              # Representative logs from a local Asya deployment
│   ├── asya-decision-router-log.txt
│   ├── asya-response-aggregator-log.txt
│   └── asya-sentiment-analyzer-log.txt
└── README.md
```
