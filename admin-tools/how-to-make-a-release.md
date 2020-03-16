<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in uncompyle6/version.py](#change-version-in-uncompyle6versionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS from ChangeLog:](#update-news-from-changelog)
- [Make sure pyenv is running and check versions](#make-sure-pyenv-is-running-and-check-versions)
- [Update NEWS from master branch](#update-news-from-master-branch)
- [Check against all versions](#check-against-all-versions)
- [Make packages and tag](#make-packages-and-tag)
- [Upload single package and look at Rst Formating](#upload-single-package-and-look-at-rst-formating)
- [Upload rest of versions](#upload-rest-of-versions)
- [Push tags:](#push-tags)

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


# make check-rst or better check via:

http://rst.ninjs.org

# Make packages and tag

    $ . ./admin-tools/make-dist.sh

Goto https://github.com/rocky/python3-trepan/releases

# Upload single package and look at Rst Formating

	$ twine check dist/trepan3k-${VERSION}*
    $ twine upload dist/trepan3k-${VERSION}-py3.3.egg

# Upload rest of versions

    $ twine upload dist/trepan3k-${VERSION}*

# Push tags:

    $ git push --tags
