apiVersion: apps/v1
kind: Deployment
metadata:
  name: poc-app
  labels:
    app: poc-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: poc-app
  template:
    metadata:
      labels:
        app: poc-app
    spec:
      containers:
      - name: poc-app
        image: gcr.io/GOOGLE_CLOUD_PROJECT/poc-app:IMAGE_TAG
        ports:
        - containerPort: 8080
