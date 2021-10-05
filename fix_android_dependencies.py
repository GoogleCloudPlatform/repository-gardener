import json
import os
import re

# These will have to be updated manually over time, there's not an
# easy way to determine the latest version.
COMPILE_SDK_VERSION = 30
TARGET_SDK_VERSION = 30
BUILD_TOOLS_VERSION = '30.0.0'

COMPILE_SDK_RE = r'compileSdkVersion[\s][\w]+'
TARGET_SDK_RE = r'targetSdkVersion[\s][\w]+'
BUILD_TOOLS_RE = r'buildToolsVersion[\s][\'\"\w\.]+'

# Depends on https://github.com/ben-manes/gradle-versions-plugin
#
# Must run this command:
# $ ./gradlew dependencyUpdates -Drevision=release -DoutputFormatter=json
RELATIVE_PATH_TO_JSON_REPORT = 'build/dependencyUpdates/report.json'

def find_gradle_files():
    """Finds all build.gradle files, recursively."""
    gradle_files = []
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.endswith('build.gradle'):
                gradle_files.append(os.path.join(root, filename))

    return gradle_files

def get_android_replacements():
    """Gets a dictionary of all android-specific replacements to be made."""
    replacements = {}

    compileSdk = 'compileSdkVersion {}'.format(COMPILE_SDK_VERSION)
    targetSdk = 'targetSdkVersion {}'.format(TARGET_SDK_VERSION)
    buildToolsVersion = 'buildToolsVersion \'{}\''.format(BUILD_TOOLS_VERSION)

    replacements[COMPILE_SDK_RE] = compileSdk
    replacements[TARGET_SDK_RE] = targetSdk
    replacements[BUILD_TOOLS_RE] = buildToolsVersion

    return replacements

def is_major_update(old_version, new_version):
    """Compares version strings to see if it's a major update."""
    old_major = old_version.split('.')[0]
    new_major = new_version.split('.')[0]

    return old_major != new_major

def get_dep_replacements(json_file):
    """Gets a dictionary of all dependency replacements to be made."""
    replacements = {}
    with open(json_file, 'r') as f:
        json_data = json.loads(f.read())

        outdated_deps = json_data['outdated']['dependencies']
        for dep in outdated_deps:
            group = dep['group']
            name = dep['name']

            curr_version = dep['version']
            new_version = dep['available']['release']

            curr_dep = '{}:{}:{}'.format(group, name, curr_version)
            new_dep = '{}:{}:{}'.format(group, name, new_version)
            replacements[curr_dep] = new_dep

    return replacements

def update_project(project_path):
    """Runs through all build.gradle files and performs replacements for individual android project."""
    replacements = {}
    replacements.update(get_android_replacements())
    replacements.update(get_dep_replacements(project_path))

    # Print all updates found
    print 'Dependency updates:'
    for (k, v) in replacements.iteritems():
        print '{} --> {}'.format(k, v)

    # Iterate through each file and replace it
    for gradle_file in find_gradle_files():
        print 'Updating dependencies for: {}'.format(gradle_file)

        new_data = ''
        with open(gradle_file, 'r') as f:
            # Perform each replacement
            new_data = f.read()
            for (k, v) in replacements.iteritems():
                new_data = re.sub(k, v, new_data)

        # Write the file
        with open(gradle_file, 'w') as f:
            f.write(new_data)

def update_all():
    """Runs through all build.gradle files and performs replacements."""

    project_root = os.getcwd()
    print 'Repo root: {}'.format(project_root)

    top_level_report = os.path.join(project_root, RELATIVE_PATH_TO_JSON_REPORT)

    if os.path.exists(top_level_report):
        print 'Update dependencies via top-level report'
        update_project(top_level_report)
    else:
        print 'Update dependencies via child-level report(s)'
        first_level_subdirectories = get_immediate_subdirectories(project_root)
        print 'List of subdirectories: {}'.format(first_level_subdirectories)

        for subdirectory in first_level_subdirectories:
            print 'subdirectory: {}'.format(subdirectory)
            subdirectory_report = os.path.join(project_root, subdirectory, RELATIVE_PATH_TO_JSON_REPORT)

            if os.path.exists(subdirectory_report):
                print '\tUpdate dependencies in subdirectory'
                update_project(subdirectory_report)
            else:
                print '\tNo report in subdirectory'

def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name)) and not name.startswith('.')]

if __name__ == '__main__':
    update_all()
