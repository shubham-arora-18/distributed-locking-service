#!/bin/bash -e

mypy distributed_locking_service

flake8 distributed_locking_service tests

black -l 100 distributed_locking_service tests --check

isort --force-single-line-imports distributed_locking_service tests scripts --check-only
