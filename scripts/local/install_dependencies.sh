#!/bin/bash
# Enable automatic exit on error
set -e

pip install --upgrade pip

export INSTALL_ADDITIONAL_DEPENDENCIES="test,dev"

sh ../shared/install_dependencies.sh

pre-commit install
