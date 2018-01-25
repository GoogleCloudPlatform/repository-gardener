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

"""This module has helpers for dealing with repo invitions."""

import logging

import github_helper


def accept_invitations():
    gh = github_helper.get_client()

    invitations = gh.session.get(
        'https://api.github.com/user/repository_invitations').json()

    for invitation in invitations:
        gh.session.patch(invitation['url'])
        logging.info('Accepted invite to {}'.format(
            invitation['repository']['full_name']))
