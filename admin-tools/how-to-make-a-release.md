<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in trepan/version.py:](#change-version-in-trepanversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS.md from ChangeLog:](#update-newsmd-from-changelog)
- [Make sure pyenv is running and check versions](#make-sure-pyenv-is-running-and-check-versions)
- [Make packages](#make-packages)
- [Check packages](#check-packages)
- [Get on PyPy](#get-on-pypy)

<!-- markdown-toc end -->
# Get latest sources:

    $ git pull

# Change version in trepan/version.py:

	$ emacs trepan/version.py
    $ source trepan/version.py
    $ echo $VERSION
    $ git commit -m"Get ready for release $VERSION" .

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

Goto https://github.com/rocky/python3-trepan/releases/new

# Check packages

	$ twine check dist/trepan3k-$VERSION*


# Get on PyPy

	$ twine upload dist/trepan3k-${VERSION}*
