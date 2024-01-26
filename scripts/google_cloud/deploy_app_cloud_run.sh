gcloud run deploy dls \
--image=asia-south1-docker.pkg.dev/distributed-locking-service/docker-repo/docker-image:version6 \
--no-allow-unauthenticated \
--port=8080 \
--region=us-central1 \
--platform managed \
--project=distributed-locking-service
