# Contributing to AI-Driven LMS

We welcome contributions to the AI-Driven Learning Management System (LMS) project! Please follow these guidelines to ensure a smooth and effective collaboration process.

## Branching Strategy

We use a Gitflow-inspired branching model:

- **`main`**: This branch holds the production-ready code. All commits to `main` should be tagged releases. Direct pushes to `main` are restricted.
- **`develop`**: This is the main development branch where all completed features and bugfixes are merged. It should always be stable and reflect the latest development version.
- **`feature/<feature-name>`**: When developing a new feature, create a branch from `develop`. For example, `feature/user-authentication`. Once the feature is complete and tested, submit a Pull Request to merge it into `develop`.
- **`bugfix/<bug-name>`**: For fixing non-critical bugs, create a branch from `develop`. For example, `bugfix/login-button-misaligned`. After fixing and testing, submit a Pull Request to `develop`.
- **`hotfix/<fix-name>`**: For critical bugs found in production, create a branch from `main`. For example, `hotfix/critical-security-vulnerability`. Once the fix is implemented and tested, it should be merged into both `main` (and tagged as a new release) and `develop` to ensure the fix is incorporated into ongoing development.

## Pull Requests (PRs)

- All contributions should be made via Pull Requests.
- Before submitting a PR, ensure your code is well-tested and adheres to any project-specific coding standards (to be defined).
- Provide a clear and descriptive title and summary for your PR. Explain the "what" and "why" of your changes.
- If your PR addresses an existing issue, link to it in the PR description.
- Ensure your branch is up-to-date with the target branch (`develop` or `main`) before submitting your PR to avoid merge conflicts. Rebase your branch if necessary.
- PRs will be reviewed by maintainers. Be prepared to address feedback and make changes.

## Coding Standards

(To be defined - will include guidelines on code style, linting, and testing.)

## Issue Tracking

(To be defined - will specify how to report bugs and suggest features.)

Thank you for contributing!
