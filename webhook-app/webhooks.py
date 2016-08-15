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

"""This module contains functions that are called whenever a particular
GitHub webhook is received."""

import logging

import github_helper
import webhook_helper


@webhook_helper.listen('ping')
def pong(data):
    return {'msg': 'pong'}


def check_for_auto_merge_trigger(text):
    """Checks the text for the phrases that should trigger an automerge."""
    text = text.lower()

    # The comment must address @dpebot directly.
    if not '@{}'.format(github_helper.github_user()) in text:
        return False

    triggers = (
        'merge on green',
        'merge when travis passes',
        'LGTM')

    for trigger in triggers:
        if trigger in text:
            return True


@webhook_helper.listen('issue_comment')
def acknowledge_merge_on_travis(data):
    """When a user comments on a pull request with one of the automerge
    triggers (e.g. merge on green), this hook will add the 'automerge'
    label."""
    if data.get('action') != 'created':
        return

    # Make sure it's a PR.
    if not github_helper.is_pull_request(data):
        return

    # If comment has trigger text.
    comment = data['comment']

    if not check_for_auto_merge_trigger(comment['body']):
        return

    # If user is a collaborator.
    gh = github_helper.get_client()
    repository = github_helper.get_repository(gh, data)

    if not repository.is_collaborator(data['sender']['login']):
        logging.info(
            '{} is not an owner and is trying to tell me what to do.'.format(
                data['sender']['login']))

    # Write a comment about it.
    pr = github_helper.get_pull_request(gh, data)
    pr.create_comment('Okay! I\'ll merge when all statuses are green.')
    pr.issue().add_labels('automerge')


@webhook_helper.listen('status')
def complete_merge_on_travis(data):
    """When all statuses on a PR are green, this hook will automatically
    merge it if it's labeled with 'automerge'."""
    # TODO: Idea - if automerge has been triggered and the status fails,
    # nag the committer to fix?

    # If it's not successful don't even bother.
    if data['state'] != 'success':
        return

    # NOTE: I'm not sure if there's a better way to do this. But, it seems
    # the status change message doesn't tell you which PR the commit is
    # from. Indeed, it's possible for a commit to actually be in multiple
    # PRs. Anyways, the idea here is to get all open PRs with the
    # tag 'automerge' and check if this commit is in that PR.
    # If so, merge.
    gh = github_helper.get_client()
    repository = github_helper.get_repository(gh, data)

    results = gh.search_issues(
        query='type:pr label:automerge status:success is:open repo:{}'.format(
            data['repository']['full_name']))

    # Covert to pull requests so we can get the commits.
    pulls = [result.issue.pull_request() for result in results]

    # See if this commit is in the PR.
    # this check isn't actually strictly necessary as the search above will
    # only return PRs that are 'green' which means we can safely merge all
    # of them. But, whatever, I'll leave it here for now anyway.
    commit_sha = data['commit']['sha']
    pulls = [
        pull for pull in pulls
        if commit_sha in [commit.sha for commit in pull.commits()]]

    # Merge!
    for pull in pulls:
        pull.merge(squash=True)

        # Delete the branch if it's in this repo. ALSO DON'T DELETE MASTER.
        if (pull.head.ref != 'master' and
                '/'.join(pull.head.repo) == data['repository']['full_name']):
            repository.ref('heads/{}'.format(pull.head.ref)).delete()
