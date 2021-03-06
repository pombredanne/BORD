#!/usr/bin/env python3
import json
import os
import requests
import sys

BASE_FORMULA_API_URL = "http://formulae.brew.sh/api/formula"
BASE_BOTTLE_URL = "https://bintray.com/homebrew/bottles/download_file?file_path="
OS = "high_sierra"

def get_dependency_list(package):
    package_name = package['name']
    print("Getting dependencies of {}.".format(package_name))
    package_url = "{}/{}.json".format(BASE_FORMULA_API_URL, package_name)
    package_json_string = requests.get(package_url).content
    package_json = json.loads(package_json_string)

    package_version = package_json["versions"]["stable"]

    # Parse the dependencies and their urls
    package_deps = []
    package_deps_names = package_json["dependencies"]
    for dep_name in package_deps_names:
        package_dep = { 'name': dep_name }
        package_deps.append(package_dep)
    
    return { 'name': package_name, 'deps': package_deps, 'version': package_version }

def package_in_dictionaries(package, dictionaries):
    for dictionary in dictionaries:
        if dictionary['name'] == package['name']:
            return True

    return False

def get_full_dependency_list(package):
    full_deps = [] # List of package dictionaries
    queue = [package] # List of package names

    while len(queue) > 0:
        subpackage = queue.pop()
        subpackage_dictionary = get_dependency_list(subpackage)
        full_deps.append(subpackage_dictionary)

        for dep in subpackage_dictionary['deps']:
            if not package_in_dictionaries(dep, full_deps) and dep not in queue:
                queue.append(dep)

    return full_deps

def download_bottles(package_dictionaries, output_dir):
    for package_dictionary in package_dictionaries:
        name = package_dictionary['name']
        version = package_dictionary['version']
        package_path = "{}-{}.{}.bottle.tar.gz".format(name, version, OS)
        url = "{}{}".format(BASE_BOTTLE_URL, package_path)

        print("Downloading bottle for {}.".format(name))
        request = requests.get(url)
        file_path = os.path.join(output_dir, package_path)
        with open(file_path, "wb") as output_file:
            output_file.write(request.content)

def main():
    if len(sys.argv) is not 2:
        print("Usage: {} <package name>".format(sys.argv[0]))
        sys.exit(1)

    package_name = sys.argv[1]
    package = { 'name': package_name }
    dependencies = get_full_dependency_list(package)

    if not os.path.exists(package_name):
        os.makedirs(package_name)
    download_bottles(dependencies, package_name)

if __name__ == "__main__":
    main()
