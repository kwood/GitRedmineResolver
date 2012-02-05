GitRedmineResolver
==================

Description
-----------
GitRedmineResolver is a git _post-receive_ hook that will scan commit messages for messages in the form of "Resolves issue #294", and will update the corresponding issue in your Redmine system.

Dependencies
------------

You have python and setuptools installed, and you should already have your repository syncing to a directory on your Redmine server.  If you don't, I recommend also doing that with a hook.

Install
-------

1. Install the dependencies

		easy_install pyactiveresource
		easy_install gitpython
	
	
2. Clone GitRedmineResolver somewhere

		cd /var/lib
		sudo mkdir gitredmine
		sudo chmod 777 gitredmine
		cd gitredmine
		git clone git@github.com:kwood/GitRedmineResolver.git

3. Set up a user in Redmine with permissions to resolve and comment on issues.

4. Set up the post-receive hook in your repository that calls GitRedmineResolver and passes stdin to it:

	Put the following in a file called post-receive inside the hooks directory in your repo:

		#!/bin/sh
		export GIT_DIR
		python /var/lib/gitredmine/GitRedmineResolver/post-receive-redmine.py http://url.to.redmine/ username password --git-dir=$GIT_DIR <&0`


How it works
------------

GitRedmineResolver will scan commit messages for strings in the form of:

(Resolving verb) (optional issue type noun) (comma or space separated list of issue numbers)

The verbs we look for are resolves/resolved and fixes/fixed.
The issue nouns are issue,task,feature, and bug
Issue numbers can be singular, or comma or space separated.  Hash signs are safe to use but optional.

Examples of matching strings:

* Resolves issue #142
* Fixes bug 148
* Fixed bugs 123 456 789
* Resolved #124 #456 #789

GitRedmineResolver will then resolve and add a comments to the corresponding issues, with a link to the commit in the Redmine repository browser.  It would be trivial to extend this script to accept more verbs that take different actions in Redmine (e.g., close issues), but since this is not part of our workflow that exercise is left to the reader.