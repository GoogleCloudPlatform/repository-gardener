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

"""Uses the google runtime config library to fetch all configuration
variables for a particular config and (optionally) updates os.environ
with these variables.

To just get the runtime configuration variables::

    >>> variables = runtimeconfig.fetch(config_name)
    {'key': 'value', ...}

To get the variables and update ``os.environ``::

    >>> runtimeconfig.fetch_and_update_environ(config_name)
    >>> os.environ['SOME_KEY']
    some_value

It will *not* replace keys already present in ``os.environ``.
"""

import base64
import logging
import os

import gcloud._helpers
import gcloud.credentials
import httplib2shim
import requests


_RUNTIMECONFIG_API_ROOT = 'https://runtimeconfig.googleapis.com/v1beta1/'

logger = logging.getLogger(__name__)


def _create_session():
    credentials = gcloud.credentials.get_credentials()
    credentials = credentials.create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(httplib2shim.Http(proxy_info=None))
    session = requests.Session()
    session.headers['Authorization'] = 'Bearer {}'.format(
        credentials.access_token)
    return session


def _list_variables(session, project, config_name):
    uri = '{root}projects/{project}/configs/{config_name}/variables'.format(
        root=_RUNTIMECONFIG_API_ROOT, project=project, config_name=config_name)
    r = session.get(uri)
    r.raise_for_status()
    return [variable['name'] for variable in r.json().get('variables', [])]


def _fetch_variable_values(session, variable_names):
    variables = {}

    # TODO: Find a way to batch this.
    for variable_name in variable_names:
        uri = '{root}{variable_name}'.format(
            root=_RUNTIMECONFIG_API_ROOT, variable_name=variable_name)
        r = session.get(uri)
        r.raise_for_status()
        data = r.json()
        # The variable name has the whole path in it, so just get the last
        # part.
        variable_name = data['name'].split('/')[-1]
        variables[variable_name] = base64.b64decode(
            data['value']).decode('utf-8')

    return variables


def fetch(config_name):
    """Fetch the variables and values for the given config.

    Returns a dictionary of variable names to values."""
    project = gcloud._helpers._determine_default_project()

    logging.info('Fetching runtime configuration {} from {}.'.format(
        config_name, project))

    session = _create_session()

    variable_names = _list_variables(session, project, config_name)
    variables = _fetch_variable_values(session, variable_names)

    return variables


def update_environ(variables):
    """Updates ``os.environ`` with the given values.

    Transforms the key name from ``some-key`` to ``SOME_KEY``.

    It will *not* replace keys already present in ``os.environ``. This means
    you can locally override whatever is in the runtime config.
    """
    for name, value in variables.items():
        compliant_name = name.upper().replace('-', '_')
        os.environ.setdefault(compliant_name, value)


def fetch_and_update_environ(config_name):
    """Fetches the variables and updates ``os.environ``."""
    variables = fetch(config_name)
    update_environ(variables)
    return variables
