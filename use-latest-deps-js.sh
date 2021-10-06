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
  (>&2 echo "This script replaces strings matching a given regex with a given string in all JavaScript files.")
  (>&2 echo "This is typically used to update JS dependencies included using an importScripts call in a ServiceWorker.")
  (>&2 echo "This script ignores the node_modules folder.")
  (>&2 echo "Usage:")
  (>&2 echo "    $0 [-d] [-i pattern] regex new_string github-user/repository-name")
  (>&2 echo "Arguments:")
  (>&2 echo "    -d: do a dry-run. Don't push or send a PR.")
  (>&2 echo "    -i: Only include files whose path match the given pattern.")
  (>&2 echo "    regex: Regex matching the original strings to replace.")
  (>&2 echo "    string: New string to replace the originals with.")
  (>&2 echo "Example:")
  (>&2 echo "    $0 \"firebase/[0-9]*\.[0-9]*\.[0-9]*/\" \"firebase/5.3.2/\" firebase/quickstart-js")
  (>&2 echo "    $0 \"firebasejs/[0-9]*\.[0-9]*\.[0-9]*/\" \"firebasejs/5.3.2/\" firebase/quickstart-js")
}

# Check for optional arguments.
DRYRUN=0

while getopts :i:d opt; do
  case $opt in
    d)
      (>&2 echo "Entered dry-run mode.")
      DRYRUN=1
      ;;
    i)
      FILE_INCLUDE_PATTERN=${OPTARG}
      (>&2 echo "Matching files in path $FILE_INCLUDE_PATTERN")
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
  (>&2 echo "Missing regex matching the original strings to replace.")
  print_usage
  exit 1
fi
if [[ -z $2 ]] ; then
  (>&2 echo "Missing new string to replace the originals with.")
  print_usage
  exit 1
fi
if [[ -z $3 ]] ; then
  (>&2 echo "Missing repo argument.")
  print_usage
  exit 1
fi
if [[ "$3" != *"/"* ]] ; then
  (>&2 echo "Repo argument needs to be of form username/repo-name.")
  print_usage
  exit 1
fi
REGEX=$1
NEW=$2
REPO=$3

# Get this script's directory.
# http://stackoverflow.com/a/246128/101923
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -x
set -e

# Find all js files that are NOT in "node_modules/".
files=0
if [[ "$FILE_INCLUDE_PATTERN" == 0 ]]; then
  files=$(find . -name "*.html")
else
  files=$(find . -name "*.html" -path "$FILE_INCLUDE_PATTERN")
fi

# Replace strings in all js files.
for file in $files; do
  sed -i -e "s|${REGEX}|${NEW}|g" "${file}"
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
