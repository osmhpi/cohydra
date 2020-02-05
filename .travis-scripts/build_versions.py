#!/usr/bin/env python3

import os
import subprocess
import json

BASE_URL = os.environ.get('DOCS_BASE_URL', 'https://osmhpi.github.io/cohydra')
BASE_URL = BASE_URL.rstrip('/') + '/'

def run(*args) -> str:
    proc = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, check=True)
    return proc.stdout.decode()

def main():
    os.chdir(os.path.dirname(__file__))

    default_branch = run('git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD')
    default_branch = default_branch.strip()[len('origin/'):]

    branches = run('git', 'for-each-ref', '--format=%(refname:lstrip=3)', 'refs/remotes/origin/')
    branches = [
        default_branch,
        *filter(lambda ref: ref not in ('HEAD', default_branch), branches.splitlines()),
    ]

    with open('versions.js', 'r') as file:
        template = file.read()

    template = template.replace('DEFAULT_BRANCH', json.dumps(default_branch))
    template = template.replace('BRANCHES', json.dumps(branches))
    template = template.replace('BASE_URL', json.dumps(BASE_URL))

    with open('../versions.js', 'w') as file:
        file.write(template)

    print('Build versions.js')
    print('  default_branch =', default_branch)
    print('  branches =', branches)
    print('  base_url =', BASE_URL)

if __name__ == '__main__':
    main()
