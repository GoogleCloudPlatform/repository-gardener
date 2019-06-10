#!/bin/bash
# Same as build-java, but works for repos that don't have a central pom

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
wget https://www-eu.apache.org/dist/maven/maven-3/3.6.1/binaries/apache-maven-3.6.1-bin.tar.gz
tar -xvzf apache-maven-3.6.1-bin.tar.gz
export MAVEN_HOME="$(pwd)/apache-maven-3.6.1-bin.tar.gz"
export PATH="${MAVEN_HOME}/bin:${PATH}"
mvn -v

chmod +x *.sh

if [ -z ${DPEBOT_BRANCH+x} ]; then
  ./clone-and-checkout.sh "${DPEBOT_REPO}"
else
  ./clone-and-checkout.sh -b "${DPEBOT_BRANCH}" "${DPEBOT_REPO}"
fi


ROOT=$(pwd)
# Get this script's directory, then up one level
# http://stackoverflow.com/a/246128/101923
PROJ_ROOT="../$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Find projects by pom and use maven to find each one
for file in **/pom.xml; do
    cd "$ROOT"
    # Navigate to the project folder.
    file=$(dirname "$file")
    cd "$file"

    # Update dependencies and plugins that use properties for version numbers.
    RULES_URI="file://$PROJ_ROOT/java-versions-rules.xml"
    mvn -U versions:use-latest-releases "-Dmaven.version.rules=$RULES_URI"
    mvn -U versions:update-properties "-Dmaven.version.rules=$RULES_URI"

done

cd "$ROOT"

# If there were any changes, test them and then push and send a PR.
set +e
if ! git diff --quiet; then
    set -e
    "${PROJ_ROOT}/commit-and-push.sh"
    "${PROJ_ROOT}/send-pr.sh" "$REPO"
fi
