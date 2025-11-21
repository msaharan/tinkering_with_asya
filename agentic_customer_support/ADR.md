# Architectural Decision Record

## 1. Cluster selection
- need: k8s cluster with GPUs enabled accessible to 2 users 
- [full search](ADR_assets/cluster_selection.md)
- decision: RunPod
    - start with RunPod because it's advertised for hackathon projects in [this](https://www.runpod.io/articles/guides/deploying-your-ai-hackathon-project-in-a-weekend-with-runpod) article
    - change later if needed
        