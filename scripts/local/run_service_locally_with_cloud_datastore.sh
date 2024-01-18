#!/bin/bash -e

export GOOGLE_CLOUD_PROJECT=qp-sandbox-inventory-4f59

uvicorn distributed_locking_service.main:app --reload

#Why running gunicorn with uvicorn is better on local machine instead of running uvicorn:
#https://fastapi.tiangolo.com/deployment/server-workers/

#Why running uvicorn is better on Kubernetes cluster instead of running gunicorn:
#https://fastapi.tiangolo.com/deployment/docker/#replication-number-of-processes
