#!/bin/bash -e

#Note: this file only works for mac-os

#run these following commented commands(one-by-one) once:
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#brew update
#brew install screen

./scripts/local/format.sh
./scripts/local/lint.sh

export DATASTORE_EMULATOR_HOST=localhost:8081
export CLOUDSDK_CORE_PROJECT=test
screen -S datastore_emulator -dm gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 --use-firestore-in-datastore-mode
pytest --cov=distributed_locking_service --cov=tests/integration_tests --cov-report=html \
-o console_output_style=progress --cov-config=.coveragerc --cov-fail-under=98 ${@}
kill -9 $(lsof -ti:8081)
