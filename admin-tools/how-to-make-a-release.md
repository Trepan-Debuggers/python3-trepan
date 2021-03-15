<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in trepan/version.py:](#change-version-in-trepanversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS.md from ChangeLog:](#update-newsmd-from-changelog)
- [Make sure pyenv is running and check versions](#make-sure-pyenv-is-running-and-check-versions)
- [Make packages](#make-packages)
- [Check packages](#check-packages)
- [Release on github](#release-on-github)
- [Release on github](#release-on-github-1)
- [Get on PyPI](#get-on-pypi)
- [Push and Pull tags:](#push-and-pull-tags)
- [Move dist files to uploaded](#move-dist-files-to-uploaded)

<!-- markdown-toc end -->
# Get latest sources:

    $ git pull

# Change version in trepan/version.py:

	$ emacs trepan/version.py
    $ source trepan/version.py
    $ echo $__version__
    $ git commit -m"Get ready for release $__version__" .

# Update ChangeLog:

    $ make ChangeLog

#  Update NEWS.md from ChangeLog:

    $ make check-short
    $ git commit --amend .
    $ git push # get CI testing going early

# Make sure pyenv is running and check versions

    $ pyenv local && source admin-tools/check-versions.sh


# Make packages

    $ . ./admin-tools/make-dist.sh

# Check packages

	$ twine check dist/trepan3k-$__version__*

# Release on github

Goto https://github.com/rocky/python3-trepan/releases/new

Set version, copy in `NEWS.md` item, upload binaries.

Now check the *tagged* release. (Checking the untagged release was previously done).

Todo: turn this into a script in `admin-tools`

	$ mkdir /tmp/gittest; pushd /tmp/gittest
	$ pyenv local 3.7.5  # or some other non-current version
	$ pip install -e git://github.com/rocky/python3-trepan.git@$__version__#egg=trepan3k
	$ trepan3k trepan3k
	$ pip uninstall trepan3k
	$ popd

# Release on github

Goto https://github.com/rocky/python2-trepan/releases/new

# Get on PyPI

	$ twine upload dist/trepan3k-${__version__}*

Check on https://pypi.org/project/trepan3k/

# Push and Pull tags:

    $ git push --tags
    $ git pull --tags

# Move dist files to uploaded

	$ mv -v dist/trepan3k-${__version__}* dist/uploaded
