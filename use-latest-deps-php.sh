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

# Find all directories containing composer.json.
directories=$(find . -name "composer.json" -not -path "**/vendor/*" -exec dirname {} \;)

# Update dependencies in all directories containing composer.json.
for DIR in $directories; do
  printf '\n### Checking dependencies in %s ###\n', "$DIR"
  pushd "$DIR"
  composer install --ignore-platform-reqs --no-dev

  updatePackages=()
  outdatedPackages=$(echo \
    "$(composer outdated 'google/*' --direct --format=json | jq '.installed' 2>/dev/null) $(composer outdated 'firebase/*' --direct --format=json | jq '.installed' 2>/dev/null)" \
    | jq -s add)

  if [[ "$outdatedPackages" != "null" ]] && [[ "$outdatedPackages" != "[]" ]] ; then
    count=$(echo "$outdatedPackages" | jq length)

    for (( i = 0; i < count; i++ ))
    do
      name=$(echo "$outdatedPackages" | jq -r --arg i "$i" '.[$i | tonumber].name')
      version=$(echo "$outdatedPackages" | jq -r --arg i "$i" '.[$i | tonumber].latest' | sed -e 's/^v//')
      if [[ "${version:0:4}" != dev- ]]; then
        updatePackages+=( "$name:^$version" )
      fi
    done

    if [ ${#updatePackages[@]} -gt 0 ]; then
      composer require --ignore-platform-reqs --update-no-dev --update-with-dependencies "${updatePackages[@]}"
    fi
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
