# Running from scratch:

Directory structure: have `asya` and `tinkering_with_asya` dirs in the same parent root dir.

Create the kind stack (sqs-s3 profile):

```sh
git clone https://github.com/deliveryhero/asya.git
cd asya/testing/e2e
make up PROFILE=sqs-s3

# configure cluster/context names same as in asya repo:
export CLUSTER_NAME="asya-e2e-sqs-s3"
kubectl config use-context "kind-${CLUSTER_NAME}"

# create custom namespace:
NAMESPACE="example-ecom"
kubectl create namespace ${NAMESPACE}

# Create SQS creds secret in your actor namespace (needed for SQS queue creation)
kubectl -n ${NAMESPACE} create secret generic sqs-secret \
  --from-literal=access-key-id=test \
  --from-literal=secret-access-key=test
```

Step into the ecommerce example root:

```sh
cd <current-repo>/merge_actor_mesh_into_asya
```

Rebuild handlers image and load into Kind (rebuild after each code change):
```sh
# Build with --no-cache to ensure fresh build during development
docker build --no-cache -t actor-mesh-asya:dev .

# Load into Kind cluster
kind load docker-image actor-mesh-asya:dev --name ${CLUSTER_NAME}

# Delete existing actor pods to force them to use the new image
# (imagePullPolicy: IfNotPresent won't reload images with same tag)
kubectl -n ${NAMESPACE} delete pods -l app=example-ecom || true
```

Deploy single actor:
```sh
ACTOR_NAME="decision-router"
# Ensure sqs-secret exists in the same namespace before applying; otherwise the Deployment won't be created
kubectl -n ${NAMESPACE} apply -f deploy/manifests/${ACTOR_NAME}.yaml
kubectl -n ${NAMESPACE} get asya ${ACTOR_NAME}
kubectl -n ${NAMESPACE} wait --for=condition=available --timeout=120s "deployment/$ACTOR_NAME"
```
(wait for 2/2 Ready)

Deploy all actors:
```sh
for file in deploy/manifests/*.yaml; do
    ACTOR_NAME=$(basename "$file" .yaml)
    echo "Deploying Actor: $ACTOR_NAME"
    kubectl -n ${NAMESPACE} apply -f "$file"
    kubectl -n ${NAMESPACE} get asya "$ACTOR_NAME"
    kubectl -n ${NAMESPACE} wait --for=condition=available --timeout=120s "deployment/$ACTOR_NAME"
done
```

For debugging, check operator logs:
```sh
kubectl -n asya-system logs -l app.kubernetes.io/instance=asya-operator -f
```

Port-forward SQS ports to localhost for testing (in a separate terminal; LocalStack runs in `asya-system`):
```sh
kubectl -n asya-system port-forward svc/localstack-sqs 4566:4566
```

Set dummy AWS creds/region (shell where you send messages):
```sh
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1
```

Send a test envelope through the full chain (sentiment → intent → context → router → response → guardrail → execution → aggregator):
```sh
KIND_SQS_BASE_URL="http://localhost:4566/000000000000"

aws --endpoint-url http://localhost:4566 sqs send-message \
  --queue-url "${KIND_SQS_BASE_URL}/asya-sentiment-analyzer" \
  --message-body '{
    "id": "demo-7",
    "route": {"actors": ["sentiment-analyzer","intent-analyzer","context-retriever","decision-router","response-generator","guardrail-validator","execution-coordinator","response-aggregator"], "current": 0},
    "payload": {
      "customer_message": "Where is my order 12345? It is one day late.",
      "customer_email": "user@example.com"
    }
  }'
```

Watch logs:
```sh
kubectl logs -n ${NAMESPACE} -l asya.sh/asya=sentiment-analyzer -c asya-runtime -f
kubectl logs -n ${NAMESPACE} -l asya.sh/asya=decision-router -c asya-runtime -f
kubectl logs -n ${NAMESPACE} -l asya.sh/asya=response-aggregator -c asya-runtime -f
```

### Clean up
```
# stop any port-forward terminals (Ctrl+C there)

# tear down the kind stack
cd asya/testing/e2e
make down PROFILE=sqs-s3

# optional: prune local docker artifacts
docker system prune -f
docker volume prune -f
```

### Debugging notes
- Pod label selector: the operator labels created pods with `asya.sh/asya=<actor>` (and `app=<actor>`). Use `kubectl get pods -n ${NAMESPACE} -l asya.sh/asya=decision-router` to find the pod; `asya.sh/actor` will return nothing.
