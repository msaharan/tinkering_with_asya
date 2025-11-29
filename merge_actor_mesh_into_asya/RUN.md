# Running from scratch:

Directory structure: have asya, tinkering_with_asya, actor-mesh-demo dirs in the same parent root dir


Create the kind stack (sqs-s3 profile):

```
cd asya/testing/e2e
make up PROFILE=sqs-s3
kubectl config use-context kind-asya-e2e-sqs-s3
```

Rebuild/load your handlers image:
```
cd ../../..
docker build -t actor-mesh-asya:dev -f tinkering_with_asya/merge_actor_mesh_into_asya/Dockerfile .
kind load docker-image actor-mesh-asya:dev --name asya-e2e-sqs-s3
```
Deploy actors:
```
kubectl apply -f tinkering_with_asya/merge_actor_mesh_into_asya/decision-router.yaml
kubectl apply -f tinkering_with_asya/merge_actor_mesh_into_asya/sentiment-analyzer.yaml
kubectl get pods -n asya-e2e -l asya.sh/asya=decision-router
kubectl get pods -n asya-e2e -l asya.sh/asya=sentiment-analyzer
```
(wait for 2/2 Ready)


Keep SQS reachable (new terminal):
```
kubectl port-forward -n asya-e2e svc/localstack-sqs 4566:4566
```

Set dummy AWS creds/region (shell where you send messages):
```
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1
```

Send a test envelope through the chain:
```
aws --region us-east-1 --endpoint-url http://localhost:4566 sqs send-message \
  --queue-url http://localhost:4566/000000000000/asya-sentiment-analyzer \
  --message-body '{
    "id": "demo-2",
    "route": {"actors": ["sentiment-analyzer","decision-router","response-generator","response-aggregator"], "current": 0},
    "payload": {
      "customer_message": "Where is my order, it is one day late?",
      "customer_email": "user@example.com"
    }
  }'
```

Watch logs:
```
kubectl logs -n asya-e2e -l asya.sh/asya=sentiment-analyzer -c asya-runtime -f
kubectl logs -n asya-e2e -l asya.sh/asya=decision-router -c asya-runtime -f
```

When finished, Ctrl+C the port-forward.
