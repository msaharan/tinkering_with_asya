# Agentic Customer Support System

A comparative implementation of an agentic customer support system using both [Asya🎭](https://github.com/deliveryhero/asya) and [Ray Serve](https://docs.ray.io/en/latest/serve/index.html).

## Overview

This project implements a multi-stage agentic customer support pipeline. For detailed use case requirements, pipeline flow, and comparison criteria, see [ADR/ADR_assets/use_case.md](ADR/ADR_assets/use_case.md).

## Project Structure

```
agentic_customer_support/
├── asya/              # Asya implementation
│   ├── handlers/      # Python handler functions
│   ├── config/        # Kubernetes CRDs and namespace
│   ├── tests/         # Unit tests
│   ├── Dockerfile     # Container image definition
│   ├── requirements.txt
│   └── README.md
├── ray_app/           # Ray Serve implementation
│   ├── handlers/      # Handler classes
│   ├── serve/         # Ray Serve deployment code
│   ├── config/        # Kubernetes deployments and namespace
│   ├── tests/         # Unit tests
│   ├── Dockerfile     # Container image definition
│   ├── requirements.txt
│   └── README.md
├── scripts/           # Deployment and testing scripts
│   ├── build_asya_images.sh
│   ├── build_ray_image.sh
│   ├── deploy_asya.sh
│   ├── deploy_ray.sh
│   └── send_test_ticket.py
├── docs/              # Documentation
│   ├── asya-deployment.md
│   ├── ray-deployment.md
│   └── asya-docs-page.md
├── examples/          # Test data and examples
│   ├── test_ticket.json
│   └── README.md
├── ADR/               # Architectural Decision Records
│   ├── ADR.md
│   └── ADR_assets/
│       ├── cluster_selection.md
│       └── use_case.md
├── COMPARISON.md      # Comparison framework and findings
├── GETTING_STARTED.md # Setup and deployment guide
├── TODO.md            # Project TODO list
├── requirements.txt   # Common dependencies
└── README.md          # This file
```

## Quick Start

For detailed setup and deployment instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

**Prerequisites:**
- Kubernetes cluster with GPUs enabled (see [ADR/ADR.md](ADR/ADR.md))
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