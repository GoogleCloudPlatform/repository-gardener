#!/usr/bin/env bash

# Copyright 2019 Google Inc. All Rights Reserved.
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
  (>&2 echo "    $0 [-d] github-user/repository-name")
  (>&2 echo "Arguments:")
  (>&2 echo "    -d: do a dry-run. Don't push or send a PR.")
}

# Check for optional arguments.
DRYRUN=0
while getopts :d opt; do
  case $opt in
    d)
      (>&2 echo "Entered dry-run mode.")
      DRYRUN=1
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

# Find all package.json files.
files=$(find . -name "composer.json" -not -path "**/vendor/*")

# Update dependencies in all package.json files.
for file in $files; do
  pushd $file

  OUTDATED=$(echo \
    "$(composer outdated 'google/*' --direct --format=json | jq '.installed') $(composer outdated 'firebase/*' --direct --format=json | jq '.installed')" \
    | jq -s add)

  if [[ "$OUTDATED" != "null" ]] ; then
    UPDATE_PACKAGES=""
    count=$(echo $OUTDATED | jq length)

    for (( i = 0; i < $count; i++ ))
    do
      name=$(echo $OUTDATED | jq -r --arg i "$i" '.[$i | tonumber].name')
      version=$(echo $OUTDATED | jq -r --arg i "$i" '.[$i | tonumber].latest')
      version="${version/v/}"
      UPDATE_PACKAGES="$UPDATE_PACKAGES $name:^$version"
    done
    composer require --update-with-dependencies $UPDATE_PACKAGES
  fi

  popd
done

set +e
if ! git diff --quiet; then
  if [[ "$DRYRUN" -eq 0 ]]; then
    set -e
    "${DIR}/commit-and-push.sh"
    "${DIR}/send-pr.sh" "$REPO"
  fi
else
  echo "No 'git diff', nothing to push."
fi
