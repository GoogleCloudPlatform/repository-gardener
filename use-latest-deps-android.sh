#!/usr/bin/env bash

# Copyright 2018 Google Inc.
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

print_usage () {
  (>&2 echo "Usage:")
  (>&2 echo "    $0 [-d] github-user/repository-name")
  (>&2 echo "Arguments:")
  (>&2 echo "    -d: do a dry-run. Don't push or send a PR.")
}

generate_dependencies_report () {
  variables_passed=$#

  if [ "${variables_passed}" -gt 0 ]; then
    dir=$1

    (>&2 echo "=========================================================================")
    (>&2 echo "Push sample path to run gradle command locally (NEW PATH, PREVIOUS PATH):")
    pushd "$dir"

    # Generate JSON dependencies report
    ./gradlew dependencyUpdates -Drevision=release -DoutputFormatter=json

    gradle_exit_code="$?"

    (>&2 echo "Pop sample path off stack, back to original path:")
    popd

    return $gradle_exit_code

  else
    # Return invalid arguments exit code.
    return 128
  fi
}

update_dependencies () {
  variables_passed=$#

  if [ "${variables_passed}" -gt 0 ]; then
    dir=$1

    # Activate a virtualenv
    virtualenv --python python2.7 env
    # shellcheck disable=SC1091
    source env/bin/activate

    # Run Android fixer script
    python "${dir}/fix_android_dependencies.py"

    # Remove the virtualenv
    rm -rf env

    return 0
  else
    # Return invalid arguments exit code.
    return 128
  fi
}

# Check for optional arguments.
DRYRUN=0
while getopts :d opt; do
  case $opt in
    d)
      (>&2 echo "Entered dry-run mode.")
      DRYRUN=1
      ;;
    \?)
      (>&2 echo "Got invalid option -$OPTARG.")
      print_usage
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))


# Check that positional arguments are set.
if [[ -z $1 ]] ; then
  (>&2 echo "Missing repo argument.")
  print_usage
  exit 1
fi
if [[ "$1" != *"/"* ]] ; then
  (>&2 echo "Repo argument needs to be of form username/repo-name.")
  print_usage
  exit 1
fi
REPO=$1


# Get this script's directory.
# http://stackoverflow.com/a/246128/101923
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set +e
set -x

generate_dependencies_report "${DIR}/"
generate_dependencies_report_exit_code="$?"

# Gradle doesn't exist at root (127 means command not found), check all child folders for android/gradle projects.
if [ $generate_dependencies_report_exit_code -eq 127 ]; then
  (>&2 echo "No Gradle at root of repo, go one level deeper for samples.")

  # Allows us to skip the loop if there aren't any folders.
  shopt -s nullglob

  # Generate list of folders in current directory.
  child_dirs=(*/)

  for child_dir in "${child_dirs[@]}"
    do
      generate_dependencies_report "${DIR}/${child_dir}"
    done
fi

set -e
update_dependencies "${DIR}"

# If there were any changes, test them and then push and send a PR.
if ! git diff --quiet; then
  if [[ "$DRYRUN" -eq 0 ]] ; then
    set -e
    "${DIR}/commit-and-push.sh"
    "${DIR}/send-pr.sh" "$REPO"
  fi
fi
