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

"""Helpers for implementing GitHub webhooks."""

from collections import defaultdict
import hashlib
import hmac
import logging
import os

import github_helper


def webhook_secret():
    return os.environ['GITHUB_WEBHOOK_SECRET'].encode('utf-8')


def webhook_url():
    return os.environ['GITHUB_WEBHOOK_URL']


def check_signature(header_signature, request_body):
    if not header_signature:
        raise ValueError('No X-Hub-Signature header.')

    algorithm, signature_digest = header_signature.split('=')

    if algorithm != 'sha1':
        raise ValueError('Unsupported digest algorithm {}.'.format(algorithm))

    body_digest = hmac.new(
        webhook_secret(), msg=request_body, digestmod=hashlib.sha1).hexdigest()

    if not hmac.compare_digest(body_digest, signature_digest):
        raise ValueError('Body digest did not match signature digest')

    return True


def create_webhook(owner, repository):
    gh = github_helper.get_client()
    repo = gh.repository(owner, repository)

    hook = repo.create_hook(
        name='web',
        config={
            'url': webhook_url(),
            'content_type': 'json',
            'secret': webhook_secret().decode('utf-8')},
        events=['*'])

    return hook

# Maps events to a list of functions to call for the webhook.
_web_hook_event_map = defaultdict(list)


def listen(event):
    """Decorator that registers a GitHub hook function."""
    def inner(f):
        _web_hook_event_map[event].append(f)
        return f
    return inner


def process(request):
    """Calls all of the functions registered for a GitHub event."""
    event = request.headers.get('X-GitHub-Event', 'ping')
    functions = _web_hook_event_map[event]

    data = request.get_json()

    logging.info('Event: {}'.format(event))

    # import json
    # guid = request.headers['X-GitHub-Delivery']
    # with open('payloads/{}.json'.format(guid), 'w') as f:
    #     json.dump(data, f, indent=2)

    for function in functions:
        result = function(data)
        if result is not None:
            return result

    return {'status': 'OK'}
