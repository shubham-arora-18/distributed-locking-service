#!/bin/bash -e

export DATASTORE_EMULATOR_HOST=localhost:8081
export CLOUDSDK_CORE_PROJECT=test
screen -S datastore_emulator -dm gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 --use-firestore-in-datastore-mode
uvicorn distributed_locking_service.main:app --reload

#Why running gunicorn with uvicorn is better on local machine instead of running uvicorn:
#https://fastapi.tiangolo.com/deployment/server-workers/

#Why running uvicorn is better on Kubernetes cluster instead of running gunicorn:
#https://fastapi.tiangolo.com/deployment/docker/#replication-number-of-processes
