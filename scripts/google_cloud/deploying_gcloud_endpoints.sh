# run the command below only for the first time
gcloud run deploy cloud-endpoint-proxy-application \
--image=gcr.io/cloudrun/hello \
--allow-unauthenticated \
--platform managed \
--region=us-central1 \
--project=prefab-sky-412817

gcloud endpoints services deploy endpoint-service-definition.yaml \
  --project prefab-sky-412817


# run the command below only for the first time
#chmod +x scripts/google_cloud/gcloud_build_image

./gcloud_build_image.sh -s cloud-endpoint-proxy-application-z4ndkzhdma-uc.a.run.app \
    -c 2024-01-31r0 -p prefab-sky-412817

gcloud run deploy cloud-endpoint-proxy-application \
  --image="gcr.io/prefab-sky-412817/endpoints-runtime-serverless:2.46.0-cloud-endpoint-proxy-application-z4ndkzhdma-uc.a.run.app-2024-01-31r0" \
  --allow-unauthenticated \
  --platform managed \
  --project=prefab-sky-412817 \
  --region=us-central1
