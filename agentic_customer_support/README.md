# Agentic Customer Support System

A comparative implementation of an agentic customer support system using both [Asya🎭](https://github.com/deliveryhero/asya) and [Ray Serve](https://docs.ray.io/en/latest/serve/index.html).

## Overview

This project implements a multi-stage customer support pipeline that processes tickets through:
1. Ticket ingestion and validation
2. Intent classification
3. Knowledge base retrieval
4. LLM response generation
5. Response validation (with dynamic routing)
6. Response formatting
7. Escalation handling

## Project Structure

```
agentic_customer_support/
├── asya/              # Asya implementation
│   ├── handlers/      # Python handler functions
│   ├── config/        # Kubernetes CRDs
│   └── README.md
├── ray/               # Ray Serve implementation
│   ├── handlers/      # Handler classes
│   ├── serve/         # Ray Serve deployment code
│   ├── config/        # Kubernetes deployments
│   └── README.md
├── examples/          # Test data and examples
├── COMPARISON.md      # Comparison framework and findings
├── ADR.md             # Architectural Decision Records
└── TODO.md            # Project TODO list
```

## Quick Start

### Prerequisites

- Kubernetes cluster with GPUs enabled (see [ADR.md](ADR.md))
- Python 3.10+
- Docker
- kubectl configured

### Asya Implementation

1. Install Asya operator (see [Asya documentation](https://github.com/deliveryhero/asya))
2. Build Docker images:
   ```bash
   docker build -t customer-support/ticket-ingester:latest -f asya/Dockerfile asya/
   ```
3. Deploy AsyncActor CRDs:
   ```bash
   kubectl apply -f asya/config/example-asyncactor.yaml
   ```

### Ray Serve Implementation

1. Install Ray operator (see [Ray documentation](https://docs.ray.io/en/latest/cluster/kubernetes/index.html))
2. Build Docker image:
   ```bash
   docker build -t customer-support/ray-serve:latest -f ray/Dockerfile ray/
   ```
3. Deploy:
   ```bash
   kubectl apply -f ray/config/example-deployment.yaml
   ```

## Development

### Local Testing

#### Asya Handlers
```bash
cd asya
python -m pytest tests/
```

#### Ray Serve
```bash
cd ray
ray serve start serve/pipeline.py
# Test endpoint
curl -X POST http://localhost:8000/support -H "Content-Type: application/json" -d @../examples/test_ticket.json
```

## Comparison

See [COMPARISON.md](COMPARISON.md) for detailed comparison of:
- Development experience
- Deployment & operations
- Performance metrics
- Reliability
- Cost analysis

## Goals

- [x] [Select cluster platform](ADR_assets/cluster_selection.md)
- [x] [Develop a minimal viable use-case](ADR_assets/use_case.md)
- [ ] Build on Asya and
- [ ] Build on Ray Serve
- [ ] Deploy on RunPod
- [ ] Validate cluster configuration
- [ ] Validate both builds
- [ ] Plan for future development

## Resources

- [Asya Documentation](https://github.com/deliveryhero/asya)
- [Ray Serve Documentation](https://docs.ray.io/en/latest/serve/index.html)
- [Use Case Details](ADR_assets/use_case.md)
