#!/bin/bash -e

gcloud auth configure-docker asia-south1-docker.pkg.dev
gcloud artifacts repositories create docker-repo --repository-format=docker --location=asia-south1
docker tag [image_name]:[tag] asia-south1-docker.pkg.dev/distributed-locking-service/docker-repo/docker-image:version1
docker push asia-south1-docker.pkg.dev/distributed-locking-service/docker-repo/docker-image:version1
