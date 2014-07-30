#!/usr/bin/env python
"""
Description
  This script will look for git commits that contain a
  string in the form of: "resolves issue 319", and will update
  the corresponding Redmine issue accordingly.
  Actually, the default regex is a bit more flexible, but feel
  free to edit it yourself.

  This is intended to be run as a git post-receive script.  You may
  either run this directly, or invoke it form another post-receive script,
  provided that the environment and stdin make it in.

Dependencies
  PyActiveResource: pip install pyactiveresource
  GitPython: pip install gitpython

Legal
  Copyright 2012 Kevin Wood <kevin@guidebook.com>
  License: MIT http://www.opensource.org/licenses/mit-license.php
"""
import os
# XXX Figure out how to pass an API key to ActiveResource instead of login

# Regex for resolved issues or merges
restring = r'(merge|merged|merging|resolve|resolves|resolved|fixes|fixed)\s?(issue|task|feature|bug)?s?\s?([#\d, ]+)'
# Regex for resolved issues or merges when branch has issue number
restring1 = r'(merge|merged|merging|resolve|resolves|resolved|fixes|fixed)'
# Regex for in progress issues or commits
cstring = r'(in progress|commit|committed|committing|working|working on|worked on|doing|did|continuing)\s?(issue|task|feature|bug)?s?\s?([#\d, ]+)'
# Regex for in progress issues or commits when branch has issue number
cstring1 = r'(in progress|commit|committed|committing|working|working on|worked on|work on|doing|did|continuing|continued|continue)'
# Regex for feedback stage or pull requests
prstring = r'(pull request|pull requested|pr|feedback|feedback for)\s?(issue|task|feature|bug)?s?\s?([#\d, ]+)'
# Regex for feedback stage or pull requests when branch has issue number
prstring1 = r'(pull request|pull requested|pr|feedback|feedback for)'
# Check to see if issue number is in the branch name
branchstring = r'([0-9]+)'

from pyactiveresource.activeresource import ActiveResource
import git
import re
import sys

regex = re.compile(restring, re.I)
cregex = re.compile(cstring, re.I)
prregex = re.compile(prstring, re.I)
regex1 = re.compile(restring1, re.I)
cregex1 = re.compile(cstring1, re.I)
prregex1 = re.compile(prstring1, re.I)
branchregex = re.compile(branchstring, re.I)


# This generator reads lines from SDTIN and returns them as 3-item lists
#   Example line from stdin:
#   0a3bf385b261cb71e176ef758c37e94639901e2d 9d3a264654c1b26f4111276d42a83a2ac4626106 refs/heads/master
def commits():
    for sLine in iter(sys.stdin.readline, ""):
        yield sLine.strip()


def quotifyString(str):
    """
    Adds a '> ' to the beginning of each line in str
    """
    return "\n".join(["> "+ line for line in str.split("\n")])


def handleMatchingIssue(issue, commit, new_status):
    quotedMessage = quotifyString(commit.message)
    if new_status == 3:
        issue_word = "Resolved by "
    elif new_status == 2:
        issue_word = "In progress by "
    else:
        issue_word = "Feedback for "
    issue.notes = issue_word + "_%s_ in revision: commit:%s\n\n%s" % (commit.author.name, commit.hexsha, quotedMessage)
    issue.status_id = new_status # Set to resolved/in progress/feedback.
    issue.save()

def processMessage(commit, IssueCls, dryRun=False):
    branchmatch = branchregex.search(branch.name)
    for line in commit.message.split("\n"):
        # Accesses different commits depending on if branch held issue number
        if branchmatch:
            match = regex1.search(line)
            cmatch = cregex1.search(line)
            prmatch = prregex1.search(line)
            numbers = branchmatch.group(1)
        else:
            match = regex.search(line)
            cmatch = cregex.search(line)
            prmatch = prregex.search(line)
        if match or cmatch or prmatch:
            if match:
                new_status = 3
                status = match.group(1)
                # Grabs issue number from commit if not in branch
                if not branchmatch:
                    numbers = match.group(3)
            elif cmatch:
                new_status = 2
                status = cmatch.group(1)
                if not branchmatch:
                    numbers = cmatch.group(3)
            else:
                new_status = 4
                status = prmatch.group(1)
                if not branchmatch:
                    numbers = prmatch.group(3)
            # Fetch a list of issues from the regex and clean them up
            issueNumbers = [num for num in numbers.replace("#","").replace(" ",",").split(",") if num]
            for issueNumber in issueNumbers:
                issue = IssueCls.find(issueNumber)
                if dryRun and issue:
                    print "Matched!"
                if issue and not dryRun:
                    handleMatchingIssue(issue, commit, new_status)

def checkCommit(rev,IssueCls):
    """ Checks all the lines in a commit for strings matching our regex"""
    if rev == 40 * "0":
        # Deleting a ref...
        return
    commit = repo.commit(newRev)
    processMessage(commit, IssueCls)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check commits for resolved Redmine issues.")
    parser.add_argument('url', type=str,
                        help="URL to the Redmine instance.")
    parser.add_argument('username', type=str,
                        help="The Redmine username to log in with.  Needs permissions to resolve and comment on issues.")
    parser.add_argument('password', type=str,
                        help="The Redmine password to log in with.")
    parser.add_argument('--git-dir', type=str,
                        help="Path to the git repo.  This is optional if GIT_DIR is defined in the environment")
    options = vars(parser.parse_args())
    gitDir = options.get('git_dir',os.environ.get('GIT_DIR'))
    if not gitDir:
        print "Missing git-dir parameter, and no GIT_DIR environment variable was available either."
        sys.exit(1)

    class Issue(ActiveResource):
        _site = options['url']
        _user = options['username']
        _password = options['password']

    repo = git.Repo(gitDir)
    # Not working, active branch is always master
    branch = repo.active_branch
    for commit in commits():
        newRev = commit
        checkCommit(newRev, Issue)