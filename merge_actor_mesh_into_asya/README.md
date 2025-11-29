# README

This project is being developed as part of the [Asya](https://github.com/deliveryhero/asya) project with the aim of developing a fully functional example exhibiting Asya's use-case through a real-world scenario.

We will take the business logic from [Actor Mesh Demo](https://github.com/msaharan/actor-mesh-demo) and integrate it into Asya such that the entire system is deployed on a local kind cluster.

Preliminary steps:
-  `make up-e2e` - make kind running locally with sqs-s3-
-  one by one, migrate actors to Asya, start with DecisionRouter for example:  take [this business logic](https://github.com/msaharan/actor-mesh-demo/blob/8ba1eeb215d3fb21b2a89384f0e0dd78d05be9d8/actors/decision_router.py#L74C9-L112), create a separate dir with asya actors , implement this DecisionRouter as a class receiving envelope (dict) instead of `message: Message`
- create this class
- create a Dockerfile (you can create one with all new handlers) so that you have docker image with these handlers
- build this image, load into kind
- deploy as asyncactor, for example:
    ```
    apiVersion: asya.sh/v1alpha1
    kind: AsyncActor
    metadata:
    name: my-actor
    spec:
    transport: sqs  # or rabbitmq
    scaling:
        enabled: true
        minReplicas: 1
        maxReplicas: 5
        queueLength: 1
    workload:
        kind: Deployment
        template:
        spec:
            containers:
            - name: asya-runtime
            image: YOUR_IMAGE:TAG
            env:
            - name: ASYA_HANDLER
                value: "module.Class.method"
    ```
- then use `aws` or `awslocal` cli to send sqs message to this actor (queue name: `asya-{actor_name}`) and check actor's runtime logs
- `kubectl get asya -n <namespace>`