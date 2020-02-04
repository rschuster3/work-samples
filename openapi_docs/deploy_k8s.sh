#! /bin/bash

set -eu

# _PROJECT_ID and _TAG_NAME are env variables at this point
# as per Dockerfile_deploy

# Point us to the correct project/zone/cluster
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone us-west1-a
gcloud container clusters get-credentials editor-microservices

# Update the deployment manifest
sed "s/GOOGLE_CLOUD_PROJECT/${PROJECT_ID}/g" k8s-deploy.yaml.tpl | \
  sed "s/IMAGE_TAG/${TAG_NAME}/g" > k8s-deploy.yaml

# Create deployment if none exists, or update if one does exist
NUM_DEPLOYMENTS=$(kubectl get deployments openapi-docs | wc -l)
if [ $NUM_DEPLOYMENTS -lt 2 ]; then
  kubectl apply -f k8s-deploy.yaml
else
  kubectl set image deployment openapi-docs \
    openapi-docs=gcr.io/${PROJECT_ID}/openapi-docs:${TAG_NAME}
fi

# Create service if none exists
NUM_SERVICES=$(kubectl get services openapi-docs | wc -l)
if [ $NUM_SERVICES -lt 2 ]; then
  kubectl apply -f k8s-service.yaml
fi
