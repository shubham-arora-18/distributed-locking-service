#!/bin/bash -e

gcloud auth configure-docker us-central1-docker.pkg.dev
gcloud artifacts repositories create distributed-locking-service --repository-format=docker --location=us-central1
docker tag [image_name]:[tag] us-central1-docker.pkg.dev/prefab-sky-412817/distributed-locking-service/docker-image:version1
docker push us-central1-docker.pkg.dev/prefab-sky-412817/distributed-locking-service/docker-image:version1
