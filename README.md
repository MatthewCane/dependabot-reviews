# Dependabot PR Review Assistant

This script helps automate the process of reviewing and approving Dependabot pull requests. It fetches open Dependabot PRs that require your review, displays relevant information, and allows you to approve and merge them quickly.

## Features

- Fetches open Dependabot pull requests where you are requested as a reviewer
- Displays PR information including repository, title, labels, and check status
- Allows you to approve PRs with a single keypress
- Uses GitHub CLI for interactions with GitHub

## Installation

This script includes [uv](https://docs.astral.sh/uv/getting-started/installation/) compatable inline script dependencies.

Alternatively, you can install the dependencies manually with `pip install rich furl`.

You will need to have the Github CLI installed and be logged in to your GitHub account.

## Usage

If you have `uv` installed, you can run the script directly with:

```bash
uv run dependabot_reviews.py
```
