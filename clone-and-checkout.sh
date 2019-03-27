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

print_usage() {
  (>&2 echo "Usage:")
  (>&2 echo "    $0 [-b branch-name] github-user/repository")
}


# Check for optional arguments.
BRANCH="dpebot-repositorygardener"
while getopts :b: opt; do
  case $opt in
    b)
      BRANCH=$OPTARG
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


# Check that environment variables are set.
if [[ -z ${DPEBOT_GIT_USER_NAME} ]] ; then
  (>&2 echo "DPEBOT_GIT_USER_NAME environment variable must be set.")
  exit 1
fi

if [[ -z ${DPEBOT_GIT_USER_EMAIL} ]] ; then
  (>&2 echo "DPEBOT_GIT_USER_EMAIL environment variable must be set.")
  exit 1
fi

if [[ -z ${DPEBOT_GITHUB_TOKEN} ]] ; then
  (>&2 echo "DPEBOT_GITHUB_TOKEN environment variable must be set.")
  exit 1
fi

# If the DPEBOT_BRANCH_BASE is not set, use master
BASE_BRANCH=${DPEBOT_BRANCH_BASE:-master}

git clone "https://dpebot:${DPEBOT_GITHUB_TOKEN}@github.com/${REPO}.git" repo-to-update
(
cd repo-to-update || exit 1
git config user.name "${DPEBOT_GIT_USER_NAME}"
git config user.email "${DPEBOT_GIT_USER_EMAIL}"

git branch "$BRANCH" "origin/$BASE_BRANCH"
git checkout "$BRANCH"
)

