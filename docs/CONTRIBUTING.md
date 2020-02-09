# Contributing

OpenAPI Spec Builder (`oapispec`) is open-source and very open to contributions.

If you're part of a corporation with an NDA, and you may require updating the license.
See Updating Copyright below

## Submitting issues

Issues are contributions in a way so don't hesitate
to submit reports.

Provide as much informations as possible to specify the issues:

- the `oapispec` version used
- a stacktrace
- installed applications list
- a code sample to reproduce the issue
- ...


## Submitting patches (bugfix, features, ...)

If you want to contribute some code:

1. Fork the official `oapispec` repository
2. Ensure an issue is opened for your feature or bug
3. Create a branch with an explicit name (like `short-feature-name` or `ISSUE#-short-name`)
4. do your work in it
5. Commit your changes. Ensure the commit message includes the issue. Also, if contributing from a corporation, be sure to add a comment with the Copyright information
6. rebase it on the master branch from the official repository (cleanup your history by performing an interactive rebase)
7. add your change to the changelog
8. submit your pull-request
9. 2 Maintainers should review the code for bugfix and features. 1 maintainer for minor changes (such as docs)
10. After review, a maintainer a will merge the PR. Maintainers should not merge their own PRs

There are some rules to follow:

- your contribution should be documented (if needed)
- your contribution should be tested and the test suite should pass successfully
- your contribution should support python 3 (do not include hacks to support python 2)
