import json
import os
import re

# These will have to be updated manually over time, there's not an
# easy way to determine the latest version.
COMPILE_SDK_VERSION = 34
TARGET_SDK_VERSION = 34
BUILD_TOOLS_VERSION = '34.0.0'

# build.gradle(.kts) files
COMPILE_SDK_RE = r'compileSdk(?:Version)?\s*=?\s*[\w]+'
TARGET_SDK_RE = r'targetSdk(?:Version)?\s*=?\s*[\w]+'
BUILD_TOOLS_RE = r'buildTools(?:Version)?\s*=?\s*[\'\"\w\.]+'

# *.versions.toml files
VERSION_RE = r'(.*)\s*=\s*"(.*)"'
DEPENDENCY_RE = r'(group|module|name|version|version.ref|id)\s*='

# Depends on https://github.com/ben-manes/gradle-versions-plugin
#
# Must run this command:
# $ ./gradlew dependencyUpdates -Drevision=release -DoutputFormatter=json
RELATIVE_PATH_TO_JSON_REPORT = 'build/dependencyUpdates/report.json'
# Default Gradle Version Catalog location
RELATIVE_PATH_TO_TOML = 'gradle/libs.versions.toml'


def find_configuration_files():
    """Finds all build configuration files, recursively."""
    gradle_files = []
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.endswith(('build.gradle', 'build.gradle.kts', 'versions.toml')):
                gradle_files.append(os.path.join(root, filename))

    return gradle_files


def get_android_replacements():
    """Gets a dictionary of all android-specific replacements to be made."""
    replacements = {}

    compile_sdk = f"compileSdk = {COMPILE_SDK_VERSION}"
    target_sdk = f"targetSdk = {TARGET_SDK_VERSION}"
    build_tools_version = f"buildToolsVersion = \"{BUILD_TOOLS_VERSION}\""

    replacements[COMPILE_SDK_RE] = compile_sdk
    replacements[TARGET_SDK_RE] = target_sdk
    replacements[BUILD_TOOLS_RE] = build_tools_version

    return replacements


def is_major_update(old_version, new_version):
    """Compares version strings to see if it's a major update."""
    old_major = old_version.split('.')[0]
    new_major = new_version.split('.')[0]

    return old_major != new_major


def get_dep_replacements(json_file, toml_deps):
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

            # For dependencies and classhpaths
            curr_dep = f"{group}:{name}:{curr_version}"
            new_dep = f"{group}:{name}:{new_version}"
            replacements[curr_dep] = new_dep

            # For the plugins block in .kts files
            curr_plugin = f'\("{group}"\) version "{curr_version}"'
            new_plugin = f'("{group}") version "{new_version}"'
            replacements[curr_plugin] = new_plugin

            # For the TOML dependencies
            module = group + ':' + name
            if module not in toml_deps:
                continue
            curr_dep = toml_deps[module]
            if 'original_line' in curr_dep:
                original_line = curr_dep['original_line']
                new_line = original_line.replace(curr_version, new_version)
                replacements[original_line] = new_line

    return replacements


def update_project(project_path, toml_path):
    """Runs through all build configuration files and performs replacements for individual android project."""
    replacements = {}
    replacements.update(get_android_replacements())
    # Open the Gradle Version Catalog file and fetch its dependencies
    toml_dependencies = get_toml_dependencies(toml_path)
    replacements.update(get_dep_replacements(project_path, toml_dependencies))

    # Print all updates found
    print("Dependency updates:")
    for (k, v) in iter(replacements.items()):
        print(f"{k} --> {v}")

    # Iterate through each file and replace it
    for config_file in find_configuration_files():
        print(f"Updating dependencies for: {config_file}")

        new_data = ''
        with open(config_file, 'r') as f:
            # Perform each replacement
            new_data = f.read()
            for (k, v) in iter(replacements.items()):
                new_data = re.sub(k, v, new_data)

        # Write the file
        with open(config_file, 'w') as f:
            f.write(new_data)


def update_all():
    """Runs through all build configuration files and performs replacements."""

    project_root = os.getcwd()
    print(f"Repo root: {project_root}")

    top_level_report = os.path.join(project_root, RELATIVE_PATH_TO_JSON_REPORT)
    toml_path = os.path.join(project_root, RELATIVE_PATH_TO_TOML)

    if os.path.exists(top_level_report):
        print("Update dependencies via top-level report")
        update_project(top_level_report, toml_path)
    else:
        print("Update dependencies via child-level report(s)")
        first_level_subdirectories = get_immediate_subdirectories(project_root)
        print(f"List of subdirectories: {first_level_subdirectories}")

        for subdirectory in first_level_subdirectories:
            print(f"subdirectory: {subdirectory}")
            subdirectory_report = os.path.join(project_root, subdirectory, RELATIVE_PATH_TO_JSON_REPORT)
            toml_path = os.path.join(project_root, subdirectory, RELATIVE_PATH_TO_TOML)

            if os.path.exists(subdirectory_report):
                print("\tUpdate dependencies in subdirectory")
                update_project(subdirectory_report, toml_path)
            else:
                print("\tNo report in subdirectory")


def get_toml_dependency(line, versions):
    original_line = line
    # skip dependencies that don't specify a version
    if 'version' not in line:
        return {}
    # Turn it into a valid JSON
    line = re.sub(DEPENDENCY_RE, r'"\1" =', line)
    value = line.split("=", 1)[1].replace("=", ":")
    dep_json = json.loads(value)
    # unspecified version means it's an internal dependency
    # we can skip version bumps for those
    if 'version' in dep_json and dep_json['version'] == 'unspecified':
        return {}
    # Fill in the group and name
    if 'module' in dep_json:
        module = dep_json.pop('module')
        [group, name] = module.split(':')
        dep_json.update({'group': group, 'name': name})
    if 'id' in dep_json:
        # 'id' indicates this is a plugin
        dep_json['group'] = dep_json.pop('id')
        dep_json['name'] = dep_json['group'] + '.gradle.plugin'

    # Fill in the current version
    if 'version.ref' in dep_json:
        dep_json['original_line'] = versions[dep_json.pop('version.ref')]['original_line']
    # if the version is inlined
    if 'version' in dep_json:
        dep_json['original_line'] = original_line
    key = dep_json.pop('group') + ':' + dep_json.pop('name')
    return {key: dep_json}


def get_toml_dependencies(toml_file):
    """Gets a dictionary of all TOML dependencies."""
    # This code assumes the [versions] block will always be first
    # True = read [versions] block; False = read [libraries] or [plugins] block
    reading_versions = True
    versions = {}
    deps = {}
    try:
        with open(toml_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                # skip empty lines or comments
                if line.strip() == '' or line.startswith("#"):
                    continue
                if '[versions]' in line:
                    reading_versions = True
                    continue
                if '[libraries]' in line or '[plugins]' in line:
                    reading_versions = False
                    continue
                # Versions
                if reading_versions:
                    version_match = re.search(VERSION_RE, line)
                    if version_match:
                        key = version_match.group(1).strip()
                        value = version_match.group(2)
                        versions[key] = {'curr_version': value, 'original_line': line}
                # Libraries and Plugins
                else:
                    deps.update(get_toml_dependency(line, versions))
    except FileNotFoundError:
        print('This project does not contain a ' + RELATIVE_PATH_TO_TOML + ' file.')
    return deps


def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name)) and not name.startswith('.')]


if __name__ == '__main__':
    update_all()
