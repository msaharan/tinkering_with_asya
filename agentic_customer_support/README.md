# Agentic Customer Support System

A comparative implementation of an agentic customer support system using both [Asya🎭](https://github.com/deliveryhero/asya) and [Ray Serve](https://docs.ray.io/en/latest/serve/index.html).

## Overview

This project implements a multi-stage agentic customer support pipeline. For detailed use case requirements, pipeline flow, and comparison criteria, see [ADR/ADR_assets/use_case.md](ADR/ADR_assets/use_case.md).

## Project Structure

```
agentic_customer_support/
├── asya/              # Asya implementation
│   ├── handlers/      # Python handler functions
│   ├── config/        # Kubernetes CRDs
│   └── README.md
├── ray_app/           # Ray Serve implementation
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

For detailed setup and deployment instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

**Prerequisites:**
- Kubernetes cluster with GPUs enabled (see [ADR.md](ADR.md))
- Python 3.10+, Docker, kubectl

**Quick Overview:**
- **Asya**: Deploy AsyncActor CRDs with handler functions
- **Ray Serve**: Deploy Ray Serve application with deployment graph

Both implementations include unit tests, Dockerfiles, and Kubernetes configurations ready for deployment.

## Comparison

See [COMPARISON.md](COMPARISON.md) for detailed comparison of:
- Development experience
- Deployment & operations
- Performance metrics
- Reliability
- Cost analysis

## Project Status

See [TODO.md](TODO.md) for the complete project checklist and progress tracking.

## Resources

- [Asya Documentation](https://github.com/deliveryhero/asya)
- [Ray Serve Documentation](https://docs.ray.io/en/latest/serve/index.html)
- [Use Case Details](ADR/ADR_assets/use_case.md)
- [Asya Deployment Runbook](docs/asya-deployment.md)
- [Ray Serve Deployment Runbook](docs/ray-deployment.md)

## Contributing to Asya Documentation

This project is part of a collaborative effort to create a real-world comparison case study for Asya. The findings from this project will be contributed back to Asya's documentation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how findings will be documented and contributed.
