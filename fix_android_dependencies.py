import json
import os
import re

# These will have to be updated manually over time, there's not an
# easy way to determine the latest version.
COMPILE_SDK_VERSION = 28
TARGET_SDK_VERSION = 28
BUILD_TOOLS_VERSION = '28.0.3'

COMPILE_SDK_RE = r'compileSdkVersion[\s][\w]+'
TARGET_SDK_RE = r'targetSdkVersion[\s][\w]+'
BUILD_TOOLS_RE = r'buildToolsVersion[\s][\'\"\w\.]+'

GROUPS_ALLOWED_MAJOR_UPDATE = [
  'com.google.android.gms',
  'com.google.firebase',
  'com.android.support',
  'com.android.support.test'
]

# Depends on https://github.com/ben-manes/gradle-versions-plugin
#
# Must run this command:
# $ ./gradlew dependencyUpdates -Drevision=release -DoutputFormatter=json
INPUT_JSON = 'build/dependencyUpdates/report.json'

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

def get_dep_replacements():
    """Gets a dictionary of all dependency replacements to be made."""
    replacements = {}
    with open(INPUT_JSON, 'r') as f:
        json_data = json.loads(f.read())

        outdated_deps = json_data['outdated']['dependencies']
        for dep in outdated_deps:
            group = dep['group']
            name = dep['name']

            curr_version = dep['version']
            new_version = dep['available']['release']

            if (is_major_update(curr_version, new_version) and
                group not in GROUPS_ALLOWED_MAJOR_UPDATE):
              print 'Skipping major update to {}:{}'.format(group, name)
              continue

            curr_dep = '{}:{}:{}'.format(group, name, curr_version)
            new_dep = '{}:{}:{}'.format(group, name, new_version)
            replacements[curr_dep] = new_dep

    return replacements

def update_all():
    """Runs through all build.gradle files and performs replacements."""
    replacements = {}
    replacements.update(get_android_replacements())
    replacements.update(get_dep_replacements())

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

if __name__ == '__main__':
  update_all()
