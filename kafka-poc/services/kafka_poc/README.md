THIS IS A TEMPORARY README FOR THIS POC

### To Run

If you need to rebuild the protobuf just do:

`protoc -I=./protos --go_out=. ./protos/hello.proto` from the `services/kafka_poc/` directory.

Now to run ...

From the `services/` directory ...

`kubectl apply -f ../kube/kafka_poc/kafka-poc-secrets.yaml`
`docker build . -t kafka-poc-producer-0.0.1 -f kafka_poc/Dockerfile_producer`
`docker build . -t kafka-poc-consumer-0.0.1 -f kafka_poc/Dockerfile_consumer`
`kubectl apply -f ../kube/kafka_poc/kafka-poc-producer.yaml`
`kubectl apply -f ../kube/kafka_poc/kafka-poc-consumer.yaml`
`kubectl get pods -l meridian-app=kafka-poc`

... get the pod name that has `consumer` in it ...

`kubectl describe pod <pod name from above>`

... make sure the pod looks good ...

`kubectl exec -it <pod name> -c nginx-container -- /bin/bash`

Inside the Nginx container do ...

`apt-get update`
`apt-get install -y curl procps`
`curl localhost`

You should see "Hello, world!".

Don't forget to clean up!

`kubectl delete deployment meridian-kafka-poc-producer`
`kubectl delete deployment meridian-kafka-poc-consumer`
`kubectl delete secret meridian-kafka-poc-config`


### What's Happening Here?

This is a REALLY SIMPLE Go service that uses the CL Kafka broker to send messages to itself. It then prints the received message in `hello.txt` which is hoped to a volume shared between `kafka-container` and `nginx-container`. This allows us to verify the Kafka messenging service worked. Alternatively I could've forced `kafka-container` to hang using `CMD tail -f /dev/null`, exec'd into it, and verified `hello.txt` was there. Either way works.


### What Do We Need To Update?

Also we need to update the `image` in the Kubernetes manifest to one that's served on Quay and remove the `imagePullPolicy`. I just added that part to get it working locally. Finally we'd need to work this into our CI/CD build.
