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

# Get latest version of the Firebase SDK on NPM
FIREBASE_SDK_INFO=$(npm view firebase --json)
FIREBASE_SDK_VER=$(node -e "console.log(${FIREBASE_SDK_INFO}['dist-tags'].latest)")

# Get latest version of FirebaseUI on NPM
FIREBASEUI_INFO=$(npm view firebaseui --json)
FIREBASEUI_VER=$(node -e "console.log(${FIREBASEUI_INFO}['dist-tags'].latest)")

(
cd repo-to-update
# Updating local/firebase hosing served Firebase SDK dependencies.
../use-latest-deps-html.sh "firebase/[0-9]*\.[0-9]*\.[0-9]*/" "firebase/${FIREBASE_SDK_VER}/" "${DPEBOT_REPO}"
../use-latest-deps-js.sh "firebase/[0-9]*\.[0-9]*\.[0-9]*/" "firebase/${FIREBASE_SDK_VER}/" "${DPEBOT_REPO}"
# Updating CDN Firebase SDK dependencies.
../use-latest-deps-html.sh "firebasejs/[0-9]*\.[0-9]*\.[0-9]*/" "firebasejs/${FIREBASE_SDK_VER}/" "${DPEBOT_REPO}"
../use-latest-deps-js.sh "firebasejs/[0-9]*\.[0-9]*\.[0-9]*/" "firebasejs/${FIREBASE_SDK_VER}/" "${DPEBOT_REPO}"
# Updating CDN FirebaseUI dependencies.
../use-latest-deps-html.sh "firebaseui/[0-9]*\.[0-9]*\.[0-9]*/" "firebaseui/${FIREBASEUI_VER}/" "${DPEBOT_REPO}"
)
