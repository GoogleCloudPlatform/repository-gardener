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

"""Helpers for interacting with the GitHub API and hook events."""

import os

import github3


def github_user():
    """Returns the bot's username."""
    return os.environ['GITHUB_USER']


def get_client():
    """Returns an authenticated github3 client."""
    gh = github3.login(
        github_user(), os.environ['GITHUB_ACCESS_TOKEN'])
    gh.session.headers.update({
        # Enable the preview API for merges and invitations
        'Accept': 'application/vnd.github.polaris-preview+json'
    })
    return gh


def get_repository(gh, data):
    """Gets the repository from hook event data."""
    return gh.repository(
        data['repository']['owner']['login'], data['repository']['name'])


def is_pull_request(data):
    """Checks if the hook event data is for a pull request."""
    return data.get('issue', {}).get('pull_request') is not None


def get_pull_request(gh, data):
    """Gets the pull request from hook event data."""
    return gh.pull_request(
        data['repository']['owner']['login'], data['repository']['name'],
        data['issue']['number'])


def accept_all_invitations(gh):
    """Accepts all invitations and returns a list of repositories."""
    # Required to access the invitations API.
    headers = {'Accept': 'application/vnd.github.swamp-thing-preview+json'}
    invitations = gh.session.get(
        'https://api.github.com/user/repository_invitations',
        headers=headers).json()

    for invitation in invitations:
        gh.session.patch(invitation['url'], headers=headers)

    return [invitation['repository'] for invitation in invitations]
