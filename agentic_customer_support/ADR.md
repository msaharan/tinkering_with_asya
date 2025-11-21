# Architectural Decision Record

## 1. Cluster selection
- need: k8s cluster with GPUs enabled accessible to 2 users 
- [full search](ADR_assets/cluster_selection.md)
- decision: RunPod
    - start with RunPod because it's advertised for hackathon projects in this [article](Deploying Your AI Hackathon Project in a Weekend with RunPod)
    - change later if needed
        