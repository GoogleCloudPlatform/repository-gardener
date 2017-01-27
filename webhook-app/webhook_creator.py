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

import logging

import github3
import github_helper
import webhook_helper


def create_webhooks():
    """Auto-creates webhooks

    * Gets all open issues assigned to the bot.
    * Checks to see if the issue is title 'add webhook'.
    * Checks the creator and the bot are both admins.
    * Creates the hook and leaves a comment.
    """

    gh = github_helper.get_client()
    issues = gh.user_issues(filter='assigned', state='open')

    for issue in issues:
        # Does someone want us to add the webhook?
        if issue.title.lower() == 'add webhook':
            logging.info('Processing issue {}'.format(issue.url))

            # Make sure the user who filed the issue is an admin.
            permission = github_helper.get_permission(
                gh, issue.repository[0],
                issue.repository[1],
                issue.user.login)

            if permission != 'admin':
                logging.info(
                    'Not installing webhook because {} is not an '
                    'admin.'.format(issue.user.login))
                return

            # Make sure we're an admin.
            repo = gh.repository(*issue.repository)

            if not repo.permissions['admin']:
                logging.info(
                    'Not installing hook because depbot is not an admin')
                # TODO: leave a comment?
                return

            # Create the webhook.
            try:
                webhook_helper.create_webhook(repo.owner, repo.name)
                issue.create_comment('Webhook added!')
            except github3.exceptions.UnprocessableEntity:
                # Webhook already exists
                logging.info('Hook already existed.')
                issue.create_comment('Webhook is already here!')

            issue.close()
