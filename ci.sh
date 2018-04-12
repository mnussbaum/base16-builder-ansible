#!/usr/bin/bash

set -o errexit
set -o nounset
set -o xtrace

for python_version in "2.7" "3.4" "3.5" "3.6"; do
  docker build -t base16-builder-ansible-test-$python_version \
    --build-arg python_version=$python_version .
  docker run base16-builder-ansible-test-$python_version
done
