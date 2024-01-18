#!/bin/bash -e

mypy distributed_locking_service

flake8 distributed_locking_service

black -l 100 distributed_locking_service --check

isort --force-single-line-imports distributed_locking_service scripts --check-only
