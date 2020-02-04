apiVersion: apps/v1
kind: Deployment
metadata:
  name: openapi-docs
  labels:
    app: openapi-docs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openapi-docs
  template:
    metadata:
      labels:
        app: openapi-docs
    spec:
      containers:
      - name: openapi-docs
        image: gcr.io/GOOGLE_CLOUD_PROJECT/openapi-docs:IMAGE_TAG
        ports:
        - containerPort: 8080
