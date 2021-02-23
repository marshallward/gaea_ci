#!/usr/bin/env python

from collections import defaultdict
import requests
import subprocess


# Fetch the main branch metadata
mom6_url = 'https://api.github.com/repos/NOAA-GFDL/MOM6'

main_params = {
    'accept': 'application/vnd.github.v3+json',
    'per_page': 100,
}

main_url = mom6_url + '/branches/main'
main_branch = requests.get(main_url, params=main_params)

main_hash = main_branch.json()['commit']['sha']

# dev/gfdl query

dev_prs_url = mom6_url + '/pulls'
dev_params = {
    'accept': 'application/vnd.github.v3+json',
    'state': 'closed',
    'base': 'dev/gfdl',
    'per_page': 100,
}

# Log the number of author PRs
contrib = defaultdict(int)

# Keep paging through results until we hit a PR which is already in main
# (but limit to 1000 PRs)
MAX_PRS = 1000
in_main = False
page = 0
while not in_main and (page * dev_params['per_page']) < MAX_PRS:
    page += 1
    dev_params['page'] = page
    dev_prs = requests.get(dev_prs_url, params=dev_params).json()

    for pr in dev_prs:
        sha = pr['merge_commit_sha']
        author = pr['user']['login']
        title = pr['title']
        num = pr['number']

        contrib[author] += 1

        # Find the branches which contain the merge
        cmd = ['git', 'branch', '--contains', sha]
        proc = subprocess.run(cmd, capture_output=True)
        rc = proc.returncode
        pr_branches = [br.decode('utf-8') for br in proc.stdout.split()]

        # Check that at least one PR is already in main
        if 'main' in pr_branches:
            in_main = True

        # If it is in dev/gfdl but not in main, then add to the report
        if rc == 0 and 'dev/gfdl' in pr_branches and 'main' not in pr_branches:
            print('- #{}: {} (@{})'.format(num, title, author))

print()
print('Contributors:')
for name in sorted(contrib, key=contrib.get, reverse=True):
    print('  - @{}: {}'.format(name, contrib[name]))
