#!/bin/bash -e

export INSTALL_ADDITIONAL_DEPENDENCIES="test, dev"

export MODULE_NAME="distributed_locking_service"

# run the following command the first time, the repo is initialized
#git submodule add git@bitbucket.org:airterra-code/cicd-tools.git cicd-tools

git submodule update --init --recursive cicd-tools

./cicd-tools/build/shared/install_proj_requirements.sh

pre-commit install
