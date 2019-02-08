#!/usr/bin/env bash

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

print_usage () {
  (>&2 echo "Usage:")
  (>&2 echo "    $0 [-d] [-p regex] github-user/repository-name")
  (>&2 echo "Arguments:")
  (>&2 echo "    -d: do a dry-run. Don't push or send a PR.")
  (>&2 echo "    -p: Only update Node packages that match the given regex")
}

# Check for optional arguments.
DRYRUN=0
REGEX=0

while getopts p:d opt; do
  case $opt in
    d)
      (>&2 echo "Entered dry-run mode.")
      DRYRUN=1
      ;;
    p)
      (>&2 echo "Limiting updating dependencies matching the regex $OPTARG.")
      REGEX=$OPTARG
      ;;
    \?)
      (>&2 echo "Got invalid option -$OPTARG.")
      print_usage
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))


# Check that positional arguments are set.
if [[ -z $1 ]] ; then
  (>&2 echo "Missing repo argument.")
  print_usage
  exit 1
fi
if [[ "$1" != *"/"* ]] ; then
  (>&2 echo "Repo argument needs to be of form username/repo-name.")
  print_usage
  exit 1
fi
REPO=$1

# Get this script's directory.
# http://stackoverflow.com/a/246128/101923
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -x
set -e

# Install some tools we will use for updates:
#  * yarn used for lockfile updates in some cases
#  * npm-check-updates provides the `ncu` tool
# Tools installed in the parent directory to avoid polluting the repo's 
# package.json file.
npm --prefix ../ install npm-check-updates
npm --prefix ../ install yarn

NODE_BIN=$(pwd)/../node_modules/.bin

# Find all package.json files.
files=$(find . -name "package.json" -not -path "**/node_modules/*")

# Update dependencies in all package.json files.
for file in $files; do
  FILE_DIR=$(dirname "${file}")

  # Move into the file's directory and run ncu, this auto-detects
  # the location of the package.json file and any .ncurc files
  if [[ "$REGEX" == 0 ]]; then
    (
    cd "${FILE_DIR}"
    "${NODE_BIN}/ncu" -u -a;
    )
  else
    (
    cd "${FILE_DIR}"
    "${NODE_BIN}/ncu" -u -a -f "${REGEX}";
    )
  fi

  # If the folder contains a package-lock.json file then run `npm install` to also update the lock file.
  if [ -f "${FILE_DIR}/package-lock.json" ]; then
    (
    cd "${FILE_DIR}"   
    npm install --package-lock-only
    )
  fi

  # If the folder contains a yarn.lock file then run `yarn install` to also update the lock file.
  if [ -f "${FILE_DIR}/yarn.lock" ]; then
    (
    cd "${FILE_DIR}"   
    "${NODE_BIN}/yarn" install --ignore-scripts --non-interactive
    )
  fi
done

set +e
if ! git diff --quiet; then
  if [[ "$DRYRUN" -eq 0 ]]; then
    "${DIR}/commit-and-push.sh"
  fi

  if [[ "$DRYRUN" -eq 0 ]]; then
    "${DIR}/send-pr.sh" "$REPO"
  fi
fi
