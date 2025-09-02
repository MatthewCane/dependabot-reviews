# Dependabot PR Review Assistant

Streamline your Dependabot pull request review process with this interactive command-line assistant. This script automates the fetching, display, and approval of Dependabot PRs, allowing you to quickly manage dependency updates and maintain your project's security and health.

## Features

- **Fetching:** Automatically retrieves open Dependabot pull requests where you are a requested reviewer.
- **Overview:** Displays essential PR information at a glance, including repository name, PR title, associated labels, and the status of CI/CD checks.
- **Approval & Merging:** Approve and merge Dependabot PRs with a single keypress, significantly reducing manual effort.

## Installation

This script requires `uv` and the GitHub CLI (`gh`).

1. **Install GitHub CLI:**
    Follow the instructions on the [GitHub CLI documentation](https://cli.github.com/) to install `gh` for your operating system.
    After installation, log in to your GitHub account:
    `gh auth login`

2. **Install Python Dependencies:**
    This script uses [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management.

## Configuration

Ensure you are logged into GitHub CLI (`gh auth login`). The script uses your GitHub CLI authentication to make changes and fetch data. No additional token configuration is required.

## Usage

Once installed and configured, you can run the script to start reviewing Dependabot PRs.

```bash
uv run dependabot_reviews
```

This will launch the interactive review assistant in your terminal. Follow the on-screen prompts to approve and merge PRs.
