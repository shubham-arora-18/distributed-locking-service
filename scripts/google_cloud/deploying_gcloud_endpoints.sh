#documentation: https://cloud.google.com/endpoints/docs/openapi/set-up-cloud-run-espv2
#great blog: https://medium.com/swlh/secure-apis-in-cloud-run-cloud-functions-and-app-engine-using-cloud-endpoints-espv2-beta-b51b1c213aea

# run the command below only for the first time
#gcloud run deploy distributed-locking-service-proxy \
#--image="gcr.io/cloudrun/hello" \
#--allow-unauthenticated \
#--platform managed \
#--region=us-central1 \
#--project=distributed-locking-service

gcloud endpoints services deploy distributed-locking-service-proxy.yaml \
  --project distributed-locking-service

# run the command below only for the first time
#gcloud services distributed-locking-service-proxy-s75wuozpva-uc.a.run.app

# run the command below only for the first time
#chmod +x scripts/google_cloud/gcloud_build_image

./scripts/google_cloud/gcloud_build_image.sh -s distributed-locking-service-proxy-s75wuozpva-uc.a.run.app \
    -c 2024-01-23r6 -p distributed-locking-service

gcloud run deploy distributed-locking-service-proxy \
  --image="gcr.io/distributed-locking-service/endpoints-runtime-serverless:2.46.0-distributed-locking-service-proxy-s75wuozpva-uc.a.run.app-2024-01-23r6" \
  --allow-unauthenticated \
  --platform managed \
  --project=distributed-locking-service \
  --region=us-central1
