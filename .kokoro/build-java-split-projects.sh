#!/bin/bash
# Same as build-java, but works for repos that don't have a central pom

set -eo pipefail
# Enables `**` to include files nested inside sub-folders
shopt -s globstar

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

# Get the dpebot project root
DPEBOT_ROOT=DIR="$(pwd)"

if [ -z ${DPEBOT_BRANCH+x} ]; then
  ./clone-and-checkout.sh "${DPEBOT_REPO}"
else
  ./clone-and-checkout.sh -b "${DPEBOT_BRANCH}" "${DPEBOT_REPO}"
fi

REPO_ROOT=$(pwd)
# Find projects by pom and use maven to find each one
for file in **/pom.xml; do
    cd "$REPO_ROOT"
    # Navigate to the project folder.
    file=$(dirname "$file")
    cd "$file"

    # Update dependencies and plugins that use properties for version numbers.
    RULES_URI="file://$DPEBOT_ROOT/java-versions-rules.xml"
    mvn -U versions:use-latest-releases "-Dmaven.version.rules=$RULES_URI"
    mvn -U versions:update-properties "-Dmaven.version.rules=$RULES_URI"

done

cd "$REPO_ROOT"

# If there were any changes, test them and then push and send a PR.
set +e
if ! git diff --quiet; then
    set -e
    "${DPEBOT_ROOT}/commit-and-push.sh"
    "${DPEBOT_ROOT}/send-pr.sh" "$REPO"
fi
