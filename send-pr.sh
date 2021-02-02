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
  (>&2 echo "    $0 github-user-or-org/repository")
}

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

if [[ -z ${DPEBOT_GITHUB_TOKEN} ]] ; then
  (>&2 echo "DPEBOT_GITHUB_TOKEN environment variable must be set.")
  exit 1
fi

# Get jq for JSON parsing
sudo apt-get install -y jq

# If the DPEBOT_BRANCH_BASE is not set, use master
BASE_BRANCH=${DPEBOT_BRANCH_BASE:-master}

# Get the current branch name.
# http://stackoverflow.com/a/19585361/101923
BRANCH=$(git symbolic-ref --short HEAD)

# Create the pull request
PR_JSON=$(curl -u "dpebot:${DPEBOT_GITHUB_TOKEN}" \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{
\"title\": \"Auto-update dependencies.\",
\"body\": \"Brought to you by your friendly [Repository Gardener](https://github.com/GoogleCloudPlatform/repository-gardener).\",
\"head\": \"${BRANCH}\",
\"base\": \"${BASE_BRANCH}\" }" \
  "https://api.github.com/repos/${REPO}/pulls")

# Label the pull request (if required)
if [[ -v $DPEBOT_GITHUB_LABEL ]] ; then
  PR_NUMBER=$(echo $PR_JSON | jq .number)
  echo "Adding label ${DPEBOT_GITHUB_LABEL} to PR ${PR_NUMBER}"

  curl -u "dpebot:${DPEBOT_GITHUB_TOKEN}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{
    \"labels\": [\"${DPEBOT_GITHUB_LABEL}\"] }" \
      "https://api.github.com/repos/${REPO}/issues/${PR_NUMBER}/labels"
fi
