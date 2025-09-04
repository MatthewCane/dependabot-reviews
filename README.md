# Dependabot PR Review Assistant

A wapper around the Github CLI, this tool aims to streamline your Dependabot pull request review process with this interactive command-line assistant. This script automates the fetching, display, and approval of Dependabot PRs, allowing you to quickly manage dependency updates and maintain your project's security and health.

## Features

- **Fetching:** Automatically retrieves open Dependabot pull requests where you are a requested reviewer.
- **Overview:** Displays essential PR information at a glance, including repository name, PR title, associated labels, and the status of CI/CD checks.
- **Approval & Merging:** Approve and merge Dependabot PRs with a single keypress, significantly reducing manual effort.

## Installation

This script requires `uv` and the GitHub CLI.

1. **Install GitHub CLI:**
    Follow the instructions on the [GitHub CLI documentation](https://github.com/cli/cli#installation) to install the CLI for your operating system. After installation, log in to your GitHub account with `gh auth login`

2. **Install uv:**
    Follow the instructions on the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) to install uv for your operating system.

3. **Install the tool using uv:**
    `uv tool install git+https://github.com/MatthewCane/dependabot-reviews`

## Usage

Once installed, you can run the script to start reviewing Dependabot PRs:

```bash
uvx dependabot-reviews
```

This will launch the interactive review assistant in your terminal. Follow the on-screen prompts to approve and merge PRs. You can also modify the PR search space with the following arguments:

| flag              | Help                                                                        |
| ----------------- | --------------------------------------------------------------------------- |
| `--repo REPO`     | filter the results to a specific repository. Searches all repos by default  |
| `--all-reviewers` | if set, will not filter PRs to only those assigned to you to review         |
