#!/bin/bash -e

export INSTALL_ADDITIONAL_DEPENDENCIES="test, dev"

export MODULE_NAME="distributed_locking_service"

git submodule update --init --recursive cicd-tools

./cicd-tools/build/shared/install_proj_requirements.sh

pre-commit install
