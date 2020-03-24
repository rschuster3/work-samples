# What's This?
This is a PoC "Hello World" app to use Cloud Build to auto-deploy a K8S cluster when we trigger via git tags or pushes.

## Two Kinds of Deploys
Notice there are two `cloudbuild.yaml` files in this microservice. One will trigger on tag deploys (`cloudbuild-tag-deploy.yaml`) and the other will trigger on push deploys (`cloudbuild-sha-deploy.yaml`). Each utilizes a different Cloud Build default variable: `$TAG_NAME` or `$COMMIT_SHA`.


## Setup
These are things you only have to do once when you're first creating this microservice!

### Permissions
Cloud Build needs permissions to use Kubernetes. This only needs to be done by one person once, but I'm noting it here for posterity/debugging.
```
export PROJECT_ID=some-project
gcloud config set project ${PROJECT_ID}
export PROJECT_NUMBER="$(gcloud projects describe ${PROJECT_ID} --format='get(projectNumber)')"
gcloud projects add-iam-policy-binding ${PROJECT_NUMBER} \
    --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role=roles/container.developer
```

### Encrypted Credentials
If they aren't already there, add encrypted Google Cloud Service Account credentials for each of our projects under `__dev_tools__/auto_deployment/`. Their file names should match our project names (that's how the manifests here know which credentials to use: by looking at Google Cloud Project ID).


## Rollbacks
You should have `gcloud` installed and authenticated, and you should have installed `kubectl` for `gcloud`:

`gcloud components install kubectl`

First get the image tag. This is either the commit hash where this work was pushed to `master` or a `sprint-x-x` branch or a git tag name.

`export IMAGE_TAG=<commit hash or git tag>`

e.g.

`export IMAGE_TAG=deploy-3-0-0`

Set the GCloud project ID

`export PROJECT_ID=<project ID>`

e.g.

`export PROJECT_ID=some-project`

Set the Kubernetes Cluster you want to deploy to:
```
gcloud config set compute/zone us-west1-a
gcloud config set project ${PROJECT_ID}
gcloud container clusters get-credentials editor-cluster
```

Deploy a new Deployment with this `IMAGE_TAG` in the selector:
```
sed "s/GOOGLE_CLOUD_PROJECT/${PROJECT_ID}/g" k8s-deploy.yaml.tpl | \
sed "s/IMAGE_TAG/${IMAGE_TAG}/g" > k8s-deploy.yaml && \
kubectl apply -f k8s-deploy.yaml
```

Verify the deploy looks good. If it doesn't, repeat the steps above with a different `IMAGE_TAG`.


## Cleanup 
If you ever wanted to delete/destroy this microservice, this document talks about cleanup steps: https://cloud.google.com/kubernetes-engine/docs/tutorials/gitops-cloud-build#delete_the_resources.
