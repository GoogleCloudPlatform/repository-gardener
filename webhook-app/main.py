# Copyright 2018 Google Inc. All Rights Reserved.
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

from flask import Flask, jsonify, request

import invitations
import webhook_creator
import webhook_helper
import webhooks
(webhooks)

logging.basicConfig(level=logging.INFO)
logging.getLogger('github3').setLevel(level=logging.WARNING)
logging.getLogger('requests').setLevel(level=logging.WARNING)
logging.getLogger('urllib3').setLevel(level=logging.WARNING)
logging.getLogger('oauth2client').setLevel(level=logging.WARNING)


app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_helper.check_signature(
        request.headers['X-Hub-Signature'],
        request.data)
    logging.info('Delivery: {}'.format(
        request.headers.get('X-GitHub-Delivery')))
    result = webhook_helper.process(request)
    return jsonify(result)


@app.route('/cron/create_webhooks')
def cron_create_webhooks():
    webhook_creator.create_webhooks()
    return 'done'


@app.route('/cron/accept_invitations')
def cron_accept_invitations():
    invitations.accept_invitations()
    return 'done'


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
