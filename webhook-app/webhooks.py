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

import time
import logging
import re

import github_helper
import webhook_helper


@webhook_helper.listen('ping')
def pong(data):
    return {'msg': 'pong'}


def check_for_auto_merge_trigger(text):
    """Checks the text for the phrases that should trigger an automerge."""
    # The comment must address @dpebot directly, on the same line
    comment = re.search(
        r'@{}\s+\b(.+)'.format(github_helper.github_user()), text, re.I)
    if not comment:
        return False
    else:
        # Just get the meat of the command
        comment = comment.group(1).strip()

    satisfaction = r'\b(pass|passes|green|approv(al|es)|happy|satisfied)'
    ci_tool = r'\b(travis|tests|statuses|kokoro|ci)\b'
    merge_action = r'\bmerge\b'
    triggers = (
        r'{}.+({}.+)?{}'.format(merge_action, ci_tool, satisfaction),
        r'{}.+{},.+{}'.format(ci_tool, satisfaction, merge_action),
        'lgtm',
    )

    return any(re.search(trigger, comment, re.I) for trigger in triggers)


@webhook_helper.listen('issue_comment')
def acknowledge_merge_on_travis(data):
    """When a user comments on a pull request with one of the automerge
    triggers (e.g. merge on green), this hook will add the 'automerge'
    label.

    Issue comment data reference:
    https://developer.github.com/v3/activity/events/types/#issuecommentevent
    """
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
    pr.create_comment(
        'Okay! I\'ll merge when all statuses are green and all reviewers '
        'approve.')
    pr.issue().add_labels('automerge')
    pr.issue().assign(github_helper.github_user())


@webhook_helper.listen('status')
def commit_status_complete_merge_on_travis(data):
    """When all statuses on a PR are green, this hook will automatically
    merge it if it's labeled with 'automerge'.

    Status data reference:
    https://developer.github.com/v3/activity/events/types/#statusevent
    """
    # TODO: Idea - if automerge has been triggered and the status fails,
    # nag the committer to fix?

    # If it's not successful don't even bother.
    if data['state'] != 'success':
        logging.info('Status not successful, returning.')
        return

    # NOTE: I'm not sure if there's a better way to do this. But, it seems
    # the status change message doesn't tell you which PR the commit is
    # from. Indeed, it's possible for a commit to actually be in multiple
    # PRs. Anyways, the idea here is to get all open PRs with the
    # tag 'automerge' and this commit in the PR.
    commit_sha = data['commit']['sha']
    gh = github_helper.get_client()
    repository = github_helper.get_repository(gh, data)

    # Sleep for about 15 seconds. Github's search index needs a few seconds
    # before it'll find the results.
    time.sleep(15)

    query = '{} type:pr label:automerge status:success is:open repo:{}'.format(
            commit_sha, data['repository']['full_name'])
    logging.info('Querying with: {}'.format(query))
    results = gh.search_issues(query=query)

    # Covert to pull requests so we can get the commits.
    pulls = [result.issue.pull_request() for result in results]
    logging.info('Found {} potential PRs: {}'.format(
        len(pulls), pulls))

    # See if this commit is in the PR.
    # this check isn't actually strictly necessary as the search above will
    # only return PRs that are 'green' which means we can safely merge all
    # of them. But, whatever, I'll leave it here for now anyway.
    pulls = [
        pull for pull in pulls
        if commit_sha in [commit.sha for commit in pull.commits()]]

    logging.info('Commit {} is present in PRs: {}'.format(
        commit_sha, pulls))

    # Merge!
    for pull in pulls:
        merge_pull_request(repository, pull, commit_sha=commit_sha)


@webhook_helper.listen('pull_request_review')
def pull_request_review_merge_on_travis(data):
    """When all approvers approve and statuses pass, this hook will
    automatically merge it if it's labeled with 'automerge'.

    Status data reference:
    https://developer.github.com/v3/activity/events/types/#pullrequestreviewevent
    """
    # If it's not successful don't even bother.
    if data['review']['state'] != 'approved':
        logging.info('Not approved, returning.')
        return

    # If the PR is closed, don't bother
    if data['pull_request']['state'] != 'open':
        logging.info('Closed, returning.')
        return

    gh = github_helper.get_client()

    repo = gh.repository(
        data['repository']['owner']['login'],
        data['repository']['name'])
    pr = repo.pull_request(data['pull_request']['number'])

    merge_pull_request(repo, pr, commit_sha=pr.head.sha)


def merge_pull_request(repo, pull, commit_sha=None):
    """Merges a pull request."""

    # only merge pulls that are labeled automerge
    labels = [label.name for label in pull.issue().labels()]
    if 'automerge' not in labels:
        logging.info('Not merging {}, not labeled automerge'.format(pull))
        return

    # only merge pulls that have all green statuses
    if not github_helper.is_sha_green(repo, commit_sha):
        logging.info('Not merging {}, not green.'.format(pull))
        return

    # Only merge pulls that have been approved!
    if not github_helper.is_pr_approved(pull):
        logging.info('Not merging {}, not approved.'.format(pull))
        return

    # By supplying the sha here, it ensures that the PR will only be
    # merged if that sha is the HEAD of the branch.
    logging.info('Merging {}.'.format(pull))
    github_helper.squash_merge_pr(pull, sha=commit_sha)

    # Delete the branch if it's in this repo. ALSO DON'T DELETE MASTER.
    if (pull.head.ref != 'master' and
            '/'.join(pull.head.repo) == repo.full_name):
        repo.ref('heads/{}'.format(pull.head.ref)).delete()
