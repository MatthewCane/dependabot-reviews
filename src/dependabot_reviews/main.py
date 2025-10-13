import asyncio
import json
import webbrowser
from argparse import ArgumentParser, Namespace
from textwrap import dedent

from furl import furl
from rich.console import Console

from dependabot_reviews.gh_cli_caller import execute_gh_command


class PullRequest:
    def __init__(self, repository: str, title: str, url: str, labels: list[dict]):
        self.repository: str = repository
        self.title: str = title
        self._url: furl = furl(url)
        self.checks_str: str = self._get_and_format_checks()
        self.labels: str = self._format_labels(labels)

    def __rich__(self) -> str:
        return dedent(f"""
            [bold purple]{self.repository}[/]
            Title: [white]{self.title}[/]
            URL: {self.url}
            Labels: {self.labels}
            Required Checks: {self.checks_str}""")

    @property
    def url(self) -> str:
        return self._url.url

    def _format_labels(self, labels: dict) -> str:
        if labels == []:
            return "[yellow]No labels[/yellow]"

        styled_labels = []
        for label in labels:
            color = label["color"]
            name = label["name"]
            styled_labels.append(f"[#{color}]{name}[/]")
        text = ", ".join(styled_labels)
        return text.strip()

    def _get_and_format_checks(self) -> str:
        result = execute_gh_command(
            f"pr view {self.url} --json statusCheckRollup"
        ).stdout

        status_checks = json.loads(result)["statusCheckRollup"]

        for check in status_checks:
            if check["conclusion"] != "SUCCESS":
                return "[red]Checks not passed[/red]"
            else:
                return "[green]Checks passed[/green]"
        return "[yellow]Checks not found[/yellow]"

    def merge(self) -> None:
        """
        Merge the PR.
        """
        execute_gh_command(
            f"pr merge {self.url}",
        )

    def close(self) -> None:
        """
        Closes the PR without merging.
        """
        execute_gh_command(f"pr close {self.url}")


async def get_pending_dependabot_prs(
    repo: str | None, requested_by_me: bool = True
) -> list[PullRequest]:
    """
    Return a list of pending dependabot PRs.
    """
    repo_str = f"--repo {repo}" if repo else ""
    requester_str = "--review-requested @me" if requested_by_me else ""

    response = execute_gh_command(
        f"search prs --state open --author 'dependabot[bot]' {repo_str} {requester_str} --json repository,title,url,labels"
    )

    pull_requests = json.loads(response.stdout)

    result = await asyncio.gather(
        *[
            asyncio.to_thread(
                PullRequest,
                pr["repository"]["nameWithOwner"],
                pr["title"],
                pr["url"],
                pr["labels"],
            )
            for pr in pull_requests
        ]
    )

    return list(result)


def check_gh_auth_status() -> bool:
    """
    Check if the user is authenticated with GitHub CLI.
    """
    try:
        return not execute_gh_command("auth status").returncode
    except RuntimeError:
        return False


def parse_args() -> Namespace:
    argparser = ArgumentParser()
    argparser.add_argument(
        "--repo",
        type=str,
        help="filter the results to a specific repository. Searches all repos by default",
    )
    argparser.add_argument(
        "--all-reviewers",
        action="store_true",
        help="if set, will not filter PRs to only those assigned to you to review",
    )
    return argparser.parse_args()


async def main() -> None:
    terminal = Console()
    args = parse_args()

    if args.all_reviewers and not args.repo:
        terminal.print(
            "[red]If --all-revewers is passed, a repo must be specified[/red]"
        )
        exit(1)
    if not check_gh_auth_status():
        terminal.print(
            "[red]You are not logged in to GitHub CLI or the Github CLI is not installed. Please run 'gh auth login' and try again.[/red]"
        )
        exit(1)

    with terminal.status("Fetching PRs..."):
        prs = await get_pending_dependabot_prs(
            repo=args.repo, requested_by_me=not args.all_reviewers
        )
    count = f"[red]{len(prs)}[/red]" if prs else "[green]0[/green]"
    terminal.print(f"Found {count} pending dependabot PRs to review")
    for pr in prs:
        terminal.print(pr)
        while True:
            terminal.print(
                "Merge? ([bold]y[/]es/[bold]c[/]lose/[bold]o[/]pen in browser/[bold]N[/]o) ",
                end="",
            )
            option = terminal.input().lower().strip()
            if option in ["y", "yes"]:
                with terminal.status("Merging..."):
                    pr.merge()
                    terminal.print(
                        "[green][bold]Merge requested (may be queued or set to automerge)[/]"
                    )
                    break
            elif option in ["c", "close"]:
                with terminal.status("Closing..."):
                    pr.close()
                    terminal.print("[red][bold]Closed[/]")
                    break
            elif option in ["o", "open"]:
                webbrowser.open(pr.url)
                terminal.print("[blue]Opened in browser[/blue]")
            else:
                terminal.print("[yellow]Skipped[/yellow]")
                break


def cli():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted")
        exit(0)
