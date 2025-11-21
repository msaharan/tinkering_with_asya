# Cluster selection search results

## 1.
You can obtain a Kubernetes (k8s) cluster with GPUs suitable for two people from several options:

1. Managed GPU Kubernetes clusters on cloud providers like Google Kubernetes Engine (GKE), AWS EKS, and Azure AKS offer GPU node pools. They allow multi-tenant setups with node pools having GPUs such as Nvidia A100 or L4. GKE supports GPU partitioning for sharing GPUs among pods/tenants. These options provide quick deployment, billing by usage, and ease of management.

2. Specialized providers like RunPod offer instant multi-node GPU clusters optimized for AI/ML workloads, deployable on demand and billed by the millisecond, which can be shared between users.

3. Open-source tools like vCluster enable creating multiple isolated virtual Kubernetes clusters on shared GPU infrastructure, enabling multi-tenancy for GPU workloads with full Kubernetes control planes per user.

4. For ultimate control and lower cost over time, you could run your own bare-metal GPU Kubernetes cluster with appropriate multi-tenancy and GPU sharing configured, but this requires hardware and setup efforts.

Examples:
- Google Cloud GKE with GPU node pools and multi-instance GPU partitions can be configured to share GPUs efficiently.
- RunPod instant clusters for GPU workloads deployed instantly.
- Open-source vCluster for creating isolated virtual K8s clusters on shared GPU cloud infrastructure.

This makes cloud-based managed Kubernetes GPU clusters or RunPod's service the best immediate option for two users needing GPU access with isolated Kubernetes environments and pay-per-use pricing. For customized multi-tenant GPU sharing, vCluster is an emerging solution.[1][2][3][4][5][6]

[1](https://www.reddit.com/r/kubernetes/comments/1lofjxh/multitenant_gpu_clusters_with_vcluster_oss_heres/)
[2](https://www.vcluster.com/blog/bare-metal-kubernetes-with-gpu-challenges-and-multi-tenancy-solutions)
[3](https://www.runpod.io/product/instant-clusters)
[4](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/gpus-multi)
[5](https://www.vcluster.com/solutions/gpu-cloud-providers)
[6](https://maddevs.io/writeups/how-to-run-pods-within-one-gpu-in-a-gke-cluster/)
[7](https://dev.to/thenjdevopsguy/sharing-a-nvidia-gpu-between-pods-in-kubernetes-4hp9)
[8](https://www.reddit.com/r/kubernetes/comments/1l9l8gz/multitenant_gpu_workloads_are_finally_possible/)
[9](https://www.qumulus.io/kubernetes-vs-vm-cloud-pricing-the-real-cost-breakdown/)
[10](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)

## 2.

To quickly get the hackathon for Asya vs Ray Serve running, here are the key steps and resources:

1. GPU Kubernetes Cluster Access:
- You can get instant GPU clusters with Kubernetes support from cloud providers like Together.ai or Runpod.io that offer multi-GPU clusters ready in minutes.
- Alternatively, set up your own Kubernetes cluster with GPU support on local or cloud infrastructure using guides like installing NVIDIA drivers and configuring Kubernetes device plugins. MicroK8s with GPU sharing is a lightweight option.
- This gives you a scalable, multi-node environment with GPUs needed for running both Asya and Ray Serve workloads.

Useful resources:
- Kubernetes GPU installation and configuration guide: dev.to article (Oct 2024)
- Instant GPU clusters with Kubernetes: together.ai and runpod.io
- Ray Serve features and use cases: an insightful list of pros/cons and capabilities
- MicroK8s GPU share setup walkthrough for lightweight local clusters

Starting with instant GPU clusters or a easy-to-configure MicroK8s cluster will minimize delay. Then choose your use-case and code the basics on Asya and Ray Serve. This will let you quickly build a side-by-side evaluation to deepen documentation and produce content for your YouTube channel or Medium article.

If you want, help can also be coordinated to find specific GPU cluster resources and finalize the use-case design for the hackathon-style evaluation.[1][2][3][4][5][6]

[1](https://dev.to/thenjdevopsguy/gpus-in-kubernetes-installation-and-configuration-51ea)
[2](https://www.runpod.io/articles/guides/deploying-your-ai-hackathon-project-in-a-weekend-with-runpod)
[3](https://www.together.ai/blog/instant-gpu-clusters)
[4](https://deep-dive-devops.com/kubernetes-gpu-share-in-microk8s-step-by-step-guide-2/)
[5](https://www.devopsschool.com/blog/top-10-ai-model-serving-frameworks-tools-in-2025-features-pros-cons-comparison/)
[6](https://www.anyscale.com/blog/deepseek-vllm-ray-google-kubernetes)
[7](https://www.youtube.com/watch?v=eBbjSfxwL30)
[8](https://opensource.org/blog/open-source-ai-and-policy-from-the-perspective-of-east-asia)
[9](https://www.reddit.com/r/kubernetes/comments/1bkmqoo/simple_explainer_on_how_gpu_allocation_to_k8s/)
[10](https://assets.ctfassets.net/xjan103pcp94/7Le2RvgnMgydY1RaD81jGM/d9cc4de603ebf46cfb5d34a06ad40e56/Ray_Open_Source-vs-Anyscale_Platform-Comparison.pdf)

