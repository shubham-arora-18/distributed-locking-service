#!/bin/bash -e

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports distributed_locking_service tests scripts

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place --remove-duplicate-keys --expand-star-imports distributed_locking_service tests scripts --exclude=__init__.py

black -l 100 distributed_locking_service scripts
