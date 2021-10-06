#!/bin/bash
# Build script for repositories with NodeJS dependencies.

set -eo pipefail

cd ${KOKORO_ARTIFACTS_DIR}/github/repository-gardener

# Kokoro should set the following environment variables.
# - DPEBOT_REPO
# - DPEBOT_GIT_USER_NAME
# - DPEBOT_GIT_USER_EMAIL="dpebot@google.com"
# Kokoro exposes this as a file, but the scripts expect just a plain variable.
export DPEBOT_GITHUB_TOKEN=$(cat ${KOKORO_GFILE_DIR}/${DPEBOT_GITHUB_TOKEN_FILE})

chmod +x *.sh

if [ -z ${DPEBOT_BRANCH+x} ]; then
  ./clone-and-checkout.sh "${DPEBOT_REPO}"
else
  ./clone-and-checkout.sh -b "${DPEBOT_BRANCH}" "${DPEBOT_REPO}"
fi

(
cd repo-to-update
if [ -z ${DPEBOT_NODE_REGEX+x} ]; then
  if [ -z ${DPEBOT_FILE_INCLUDE_PATTERN+x} ]; then
    ../use-latest-deps-node.sh "${DPEBOT_REPO}"
  else
    ../use-latest-deps-node.sh -i "$DPEBOT_FILE_INCLUDE_PATTERN" "${DPEBOT_REPO}"
else
  if [ -z ${DPEBOT_FILE_INCLUDE_PATTERN+x} ]; then
    ../use-latest-deps-node.sh -p "${DPEBOT_NODE_REGEX}" "${DPEBOT_REPO}"
  else
    ../use-latest-deps-node.sh -i "$DPEBOT_FILE_INCLUDE_PATTERN" -p "${DPEBOT_NODE_REGEX}" "${DPEBOT_REPO}"
fi
)
