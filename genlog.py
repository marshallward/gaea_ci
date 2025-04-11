#!/usr/bin/env python

from collections import defaultdict
import requests
import subprocess

# Debugging...?
verbose = False

# Always accept (perhaps because they were accepted outside of GitHub)
# TODO: Set by command-line?
always_accept = [
    520,
    531,
    540,
    565,
    614,
]

# Fetch the main branch metadata
gfdl_url = 'https://api.github.com/repos/NOAA-GFDL/MOM6'
main_url = 'https://api.github.com/repos/mom-ocean/MOM6'

main_params = {
    'accept': 'application/vnd.github.v3+json',
    'per_page': 100,
}

main_api_url = main_url + '/branches/main'
main_branch = requests.get(main_api_url, params=main_params)

main_hash = main_branch.json()['commit']['sha']

# dev/gfdl query

dev_prs_url = gfdl_url + '/pulls'
dev_params = {
    'accept': 'application/vnd.github.v3+json',
    'state': 'closed',
    'base': 'dev/gfdl',
    'per_page': 100,
}

# Log the number of author PRs
contrib = defaultdict(int)

# Store closed PRs for review
closed_prs = []

# Keep paging through results until we hit a PR which is already in main
# (but limit to 1000 PRs)
MAX_PRS = 10 * dev_params['per_page']
in_main = False
page = 0
while not in_main and (page * dev_params['per_page']) < MAX_PRS:
    page += 1
    dev_params['page'] = page
    if verbose:
        print('Requesting page {0}...'.format(page))
    dev_prs = requests.get(dev_prs_url, params=dev_params).json()
    # NOTE: dev_prs is a list of the 100 most recent PRs to dev/gfdl
    for pr in dev_prs:
        sha = pr['merge_commit_sha']
        author = pr['user']['login']
        title = pr['title']
        num = pr['number']

        if verbose:
            print()
            print("PR: {}".format(num))
            print("  title: {}".format(title))
            print("  author: {}".format(author))
            print("  hash: {}".format(sha))

        # Find the branches which contain the merge
        # NOTE: This is an oddly local operation: How do I know that the local
        #   branches are equal to the remote branches?
        cmd = ['git', 'branch', '--contains', sha]
        proc = subprocess.run(cmd, capture_output=True)
        rc = proc.returncode
        pr_branches = [br.decode('utf-8') for br in proc.stdout.split()]

        # A nonzero return code generally means that the commit was unmerged.
        # (But I suppose there are other reasons?)
        pr_missing = rc == 0

        # Check if PR has been accepted and merged by dev/gfdl
        pr_merged = 'dev/gfdl' in pr_branches

        # Check if PR has already been merged to main
        pr_in_main = 'main' in pr_branches

        if pr_in_main:
            # If any PR is main, then we assume that we are done looking for
            # PRs and signal that we will stop requesting pages from GitHub.
            # XXX: This is dodgy but also the current approach.
            if pr_in_main:
                in_main = True
        else:
            # If it is in dev/gfdl but not in main, then add to the report
            # TODO: Pipe to output file?
            if pr_merged or num in always_accept:
                print('- #{}: {} (@{})'.format(num, title, author))
                # TODO: Can I get *all* authors in a PR?
                contrib[author] += 1
            else:
                pr = {'num': num, 'title': title, 'author': author, 'sha': sha}
                closed_prs.append(pr)

print()
print('Contributors:')
for name in sorted(contrib, key=contrib.get, reverse=True):
    print('  - @{}: {}'.format(name, contrib[name]))

gfdl_url_user = gfdl_url.replace("api.", "").replace("/repos/", "/")

if closed_prs:
    # The idea here is to inspect and review each PR via the provided URL.
    # If there was an error, then add it to `always_accept` and re-run the
    # script.
    print()
    print('Closed PRs:')
    for pr in closed_prs:
        print()
        print("PR: {}".format(pr['num']))
        print("  title: {}".format(pr['title']))
        print("  author: {}".format(pr['author']))
        #print("  hash: {}".format(pr['sha']))
        print("  URL: {}".format(gfdl_url_user + "/pull/" + str(pr['num'])))
