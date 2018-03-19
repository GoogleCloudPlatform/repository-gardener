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

import json
import os

import github3


def github_user():
    """Returns the bot's username."""
    return os.environ['GITHUB_USER']


def get_client():
    """Returns an authenticated github3 client."""
    gh = github3.login(
        github_user(), os.environ['GITHUB_ACCESS_TOKEN'])
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


def get_pr_requested_reviewers(pr):
    """Gets a list of all requested reviewers on a PR."""
    url = (
        'https://api.github.com/repos/{}/{}/pulls/{}'
        '/requested_reviewers'.format(
            pr.repository[0], pr.repository[1], pr.number))

    reviewers = pr.session.get(url).json()

    return reviewers.get('users', [])


def get_pr_reviews(pr):
    """Gets a list of all submitted reviews on a PR. Does not list requested
    reviews."""
    # Required to access the PR review API.
    headers = {'Accept': 'application/vnd.github.black-cat-preview+json'}
    reviews = pr.session.get(
        'https://api.github.com/repos/{}/{}/pulls/{}/reviews'.format(
            pr.repository[0], pr.repository[1], pr.number),
        headers=headers).json()

    return reviews


def get_pr_required_statuses(pr):
    """Gets a list off all of the required statuses for a PR to be merged."""
    statuses = pr.session.get(
        'https://api.github.com/repos/{}/branches/{}/protection/'
        'required_status_checks/contexts'.format(
            pr.repository, pr.base.ref)).json()

    return statuses


def get_pr_statuses(pr):
    """Gets a list of currently reported statuses for the commit."""
    statuses = pr.session.get(
        'https://api.github.com/repos/{}/commits/{}/'
        'statuses'.format(
            pr.repository, pr.head.sha)).json()

    return [status['context'] for status in statuses]


def has_required_statuses(pr):
    """Returns True if the PR has all the protected statuses present."""

    required = get_pr_required_statuses(pr)

    if not len(required):
        return True

    listed = get_pr_statuses(pr)

    return set(required).issubset(set(listed))


def is_pr_approved(pr):
    """True if the PR has been completely approved."""
    review_requests = get_pr_requested_reviewers(pr)

    if not len(review_requests):
        return True

    reviews = get_pr_reviews(pr)

    approved_users = [
        review['user']['login'] for review in reviews
        if review['state'] == 'APPROVED']

    requested_users = [user['login'] for user in review_requests]

    return set(approved_users) == set(requested_users)


def is_sha_green(repo, sha):
    url = 'https://api.github.com/repos/{}/{}/commits/{}/status'.format(
        repo.owner.login, repo.name, sha)
    result = repo.session.get(url).json()

    return result['state'] == 'success'


def get_permission(gh, owner, repo, user):
    # Required to access the collaborators API.
    headers = {'Accept': 'application/vnd.github.korra-preview'}

    result = gh.session.get(
        'https://api.github.com/repos/{}/{}/collaborators'
        '/{}/permission'.format(owner, repo, user),
        headers=headers).json()

    return result['permission']


def squash_merge_pr(pr, sha):
    data = {
        'sha': sha,
        'merge_method': 'squash'
    }

    response = pr.session.put(
        'https://api.github.com/repos/{}/{}/pulls/{}/merge'.format(
            pr.repository[0], pr.repository[1], pr.number),
        json=data)

    response.raise_for_status()

    return response.json()
