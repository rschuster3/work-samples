### To Test In Cental Lite

If you need to rebuild the protobuf just do:

`make build` from the `services/kafka_poc/` directory.

Now to run ...

From the `services/` directory ...

```
kubectl apply -f ../kube/kafka-poc-config.yaml
docker build . -t kafka-poc-producer-0.0.1 -f kafka_poc/Dockerfile_producer
docker build . -t kafka-poc-consumer-0.0.1 -f kafka_poc/Dockerfile_consumer
kubectl apply -f ../kube/kafka-poc-producer.yaml
kubectl apply -f ../kube/kafka-poc-consumer.yaml
kubectl get pods -l meridian-app=kafka-poc
```

... get the pod name that has `consumer` in it ...

`kubectl describe pod <pod name from above>`

... make sure the pod looks good ...

Now log the pod ...

`kubectl logs <pod name from above>`

You should see a bunch of "Hello world" messages.

`{"level":"info","ts":1585164022.309797,"caller":"consumer/main.go:54","msg":"Hello, world!","type":"kafka_message"}`

Don't forget to clean up!

```
kubectl delete deployment meridian-kafka-poc-producer
kubectl delete deployment meridian-kafka-poc-consumer
kubectl delete configmap meridian-kafka-poc-config
```


### What's Happening Here?

This is a Go app that uses a Kafka broker to send messages to from a producer service to a consumer service. It requests info about the Kafka broker and uses that to set up a connection to a subscription topic. The producer prints messages to the topic and the consumer grabs/logs them.
