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

3. Set up the post-receive hook in your repository that calls GitRedmineResolver and passes stdin to it:

	Put the following in hooks/post-receive inside your repo directory:

		#!/bin/sh
		export GIT_DIR
		python /var/lib/gitredmine/GitRedmineResolver/post-receive-redmine.py http://url.to.redmine/ username password --git-dir=$GIT_DIR <&0`
