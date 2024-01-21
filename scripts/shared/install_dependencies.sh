#!/bin/bash
# Enable automatic exit on error
set -e

pip install --upgrade pip

export MODULE_NAME="distributed_locking_service"

if [[ -f requirements.txt && -f pyproject.toml ]]
then
    echo "found both requirements.txt and pyproject.toml"
    exit 1
fi

#installing requirements
if [ -f requirements.txt ]
then
    echo "Installing depedencies from requirements.txt"
    pip install -r requirements.txt
    if [ $INSTALL_ADDITIONAL_DEPENDENCIES ]
    then
        echo "Additional dependencies: $INSTALL_ADDITIONAL_DEPENDENCIES"
        IFS=',' read -r -a dependencies <<< "$INSTALL_ADDITIONAL_DEPENDENCIES"
        for dependency_name in "${dependencies[@]}"
        do
            if [ -f requirements-$dependency_name.txt ]
            then
                echo "Installing depedencies from requirements-$dependency_name.txt"
                pip install -r requirements-$dependency_name.txt
            else
                echo "Skipping [$dependency_name], as the file 'requirements-$dependency_name.txt' is missing."
            fi
        done
    fi
elif [ -f pyproject.toml ]
then
    echo "Installing dependencies from pyproject.toml"
    pip install .
    if [ $INSTALL_ADDITIONAL_DEPENDENCIES ]
    then
        IFS=',' read -r -a dependencies <<< "$INSTALL_ADDITIONAL_DEPENDENCIES"
        for dependency_name in "${dependencies[@]}"
        do
          echo "Installing $dependency_name dependencies from pyproject.toml"
          pip install $MODULE_NAME\[$dependency_name\]
        done
    fi
else
    echo "Unable to find any source for dependencies"
    exit 1
fi
