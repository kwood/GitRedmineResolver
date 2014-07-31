GitRedmineResolver
==================

Description
-----------
GitRedmineResolver is a git _post-receive_ hook that will scan commit messages for messages in the form of "Resolves issue #294" and will update the corresponding issue in your Redmine system.

How it works
------------

GitRedmineResolver will scan your commit messages after you push for strings in the form of:

(Action verb) (optional issue type noun) (comma or space separated list of issue numbers)

The verbs we look for for marking issues as "resolved" are merge, merged, merging, resolve, resolves, resolved, fix, fixes, fixed, close, closed, closing, done, finish, finishing, finished.
The verbs we look for for marking issues as "in progress" are in progress, commit, committed, committing, working, working on, worked on, doing, did, continuing, continued, continue, start, started, starting.
Issue numbers can be singular, or comma or space separated.  Hash signs are safe to use but optional.

Examples of matching strings for resolving:
* Resolves #142
* Fixes bug 148
* Merged feature #123 456 789

Examples of matching strings for in progress:
* In progress issue #142
* Committed bug 148
* Working feature #123 456 789

GitRedmineResolver will then resolve and add a comment to the corresponding issues, with a link to the commit in the Redmine repository browser.  If you use a resolving verb and issue number while the active branch is master, the bridge will close your issue rather than just marking it as resolved, assuming that you are done.


Dependencies
------------

You have python and setuptools installed, and you should already have your repository syncing to a directory on your Redmine server.  If you don't, I recommend also doing that with a hook.

Install
-------

1. Install the dependencies (pyactiveresource and gitpython)

		pip install -r requirements.txt


2. Clone GitRedmineResolver somewhere

		cd /var/lib
		sudo mkdir gitredmine
		sudo chmod 777 gitredmine
		cd gitredmine
		git clone git@github.com:kwood/GitRedmineResolver.git

3. Set up a user in Redmine with permissions to resolve and comment on issues.

4. Set up the post-receive hook in your repository that calls GitRedmineResolver and passes stdin to it:

	Move the post-receive file into your hook directory and make sure to edit the information so it matches you.
	Clarification: this hook directory is where you are pushing to, whether you set up a local repo or one on our servers.
	In the hooks folder after creating or moving the post-receive file there, run this.

		chmod +x post-receive
