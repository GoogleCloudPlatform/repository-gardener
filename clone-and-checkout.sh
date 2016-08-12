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

if [[ -z $1 ]] ; then
  (>&2 echo "Missing repo argument.")
  (>&2 echo "Usage:")
  (>&2 echo "    $0 repository-name")
  (>&2 echo "Where repository-name is some repo under the GoogleCloudPlatform")
  (>&2 echo "org with an identically-named fork.")
  exit 1
fi
REPO=$1

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

BRANCH="dpebot-repositorygardener"

# TODO: Support other orgs (such as codelabs).
git clone "https://dpebot:${DPEBOT_GITHUB_TOKEN}@github.com/GoogleCloudPlatform/${REPO}.git" repo-to-update
(
cd repo-to-update || exit 1
git config user.name "${DPEBOT_GIT_USER_NAME}"
git config user.email "${DPEBOT_GIT_USER_EMAIL}"

git branch "$BRANCH" origin/master
git checkout "$BRANCH"
)

