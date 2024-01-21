#!/bin/bash

# Bash "strict mode", to help catch problems and bugs in the shell
# script. Every bash script you write should include this. See
# http://redsymbol.net/articles/unofficial-bash-strict-mode/ for
# details.
set -euo pipefail

#clean up before starting update process
apt-get autoclean
apt-get clean
apt-get autoremove

# Tell apt-get we're never going to be able to give manual
# feedback:
export DEBIAN_FRONTEND=noninteractive

# Update the package listing, so we know what package exist:
apt-get update

# Update the package listing, so we know what package exist:
apt-get dist-upgrade -qq

# Install security updates:
apt-get -y upgrade

# Install a new package, without unnecessary recommended packages:
apt-get -y install --no-install-recommends syslog-ng

apt-get install -y curl

# Delete cached files we don't need anymore:
apt-get clean
rm -rf /var/lib/apt/lists/*
