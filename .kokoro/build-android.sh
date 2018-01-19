#!/bin/bash
# Build script for repositories with Android dependencies.

set -eo pipefail

cd ${KOKORO_ARTIFACTS_DIR}/github/repository-gardener

# Kokoro should set the following environment variables.
# - DPEBOT_REPO
# - DPEBOT_GIT_USER_NAME
# - DPEBOT_GIT_USER_EMAIL="dpebot@google.com"
# Kokoro exposes this as a file, but the scripts expect just a plain variable.
export DPEBOT_GITHUB_TOKEN=$(cat ${KOKORO_GFILE_DIR}/${DPEBOT_GITHUB_TOKEN_FILE})

chmod +x *.sh

./clone-and-checkout.sh "${DPEBOT_REPO}"

(
cd repo-to-update
../use-latest-deps-android.sh "${DPEBOT_REPO}"
)
