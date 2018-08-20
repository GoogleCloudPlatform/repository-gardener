#!/bin/bash
# Build script for repositories with Java dependencies.

set -eo pipefail

cd ${KOKORO_ARTIFACTS_DIR}/github/repository-gardener

# Kokoro should set the following environment variables.
# - DPEBOT_REPO
# - DPEBOT_GIT_USER_NAME
# - DPEBOT_GIT_USER_EMAIL="dpebot@google.com"
# Kokoro exposes this as a file, but the scripts expect just a plain variable.
export DPEBOT_GITHUB_TOKEN=$(cat ${KOKORO_GFILE_DIR}/${DPEBOT_GITHUB_TOKEN_FILE})

# Install some extra packages needed by java-docs-samples
sudo apt-get install -y expect shellcheck

# Install Maven
wget http://www-us.apache.org/dist/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz
tar -xvzf apache-maven-3.3.9-bin.tar.gz
export MAVEN_HOME="$(pwd)/apache-maven-3.3.9"
export PATH="${MAVEN_HOME}/bin:${PATH}"
mvn -v

chmod +x *.sh

if [ -z ${DPEBOT_BRANCH+x} ]; then
  ./clone-and-checkout.sh "${DPEBOT_REPO}"
else
  ./clone-and-checkout.sh -b "${DPEBOT_BRANCH}" "${DPEBOT_REPO}"
fi

(
cd repo-to-update
../use-latest-deps-java.sh "${DPEBOT_REPO}"
)
