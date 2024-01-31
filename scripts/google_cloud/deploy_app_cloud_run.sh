gcloud run deploy backend-web-application \
--image=us-central1-docker.pkg.dev/prefab-sky-412817/distributed-locking-service/docker-image:version1 \
--no-allow-unauthenticated \
--port=8080 \
--region=us-central1 \
--platform managed \
--project=prefab-sky-412817
