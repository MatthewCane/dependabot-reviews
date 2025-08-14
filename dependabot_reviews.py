#! /usr/bin/env uv run --script

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich",
#     "furl",
# ]
# ///
import asyncio
import subprocess
import json
from rich.console import Console
from furl import furl


class PullRequest:
    def __init__(self, repository: str, title: str, url: str, labels: list[str]):
        self.repository: str = repository
        self.title: str = title
        self._url: furl = furl(url)
        self.labels_str: str = self._format_labels(labels)
        self.checks_str: str = self._get_and_format_checks()

    def __repr__(self) -> str:
        return f"PullRequest(repository='{self.repository}', title='{self.title}', url='{self.url}', labels='{self.labels}')"

    @property
    def url(self) -> str:
        return self._url.url

    def _format_labels(self, labels: list) -> str:
        if labels == []:
            return ""

        return str("[" + ",".join([label["name"] for label in labels]) + "]")

    def _get_and_format_checks(self) -> str:
        status_checks = execute_gh_command(
            f"pr view {self.url} --json statusCheckRollup"
        )["statusCheckRollup"]

        if status_checks == []:
            return "[yellow] Checks not found[/yellow]"
        for check in status_checks:
            if check["conclusion"] != "SUCCESS":
                return "[red] Checks not passed[/red]"
            else:
                return "[green] Checks passed[/green]"


def execute_gh_command(command: str, return_response: bool = True) -> dict | None:
    """
    Execute a Github CLI command and return the JSON output.
    """
    try:
        result = subprocess.run(
            f"gh {command}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        if return_response:
            return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with exit code {e.returncode}\n"
        error_message += f"stdout: {e.stdout}\n"
        error_message += f"stderr: {e.stderr}"
        raise RuntimeError(error_message) from e
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON output: {e}\nOutput: {result.stdout}"
        ) from e


async def get_pending_dependabot_prs() -> list[PullRequest]:
    """
    Return a list of pending dependabot PRs.
    """
    response = execute_gh_command(
        "search prs --state open --author 'dependabot[bot]'  --review-requested @me --json repository,title,url,labels"
    )

    return await asyncio.gather(
        *[asyncio.to_thread(PullRequest, pr["repository"]["nameWithOwner"], pr["title"], pr["url"], pr["labels"]) for pr in response]
    )
    


def approve_pr(pr: str) -> None:
    """
    Approves a PR with the message "@dependabot merge".
    """
    execute_gh_command(
        f"pr review {pr.url} --approve --body '@dependabot merge'",
        return_response=False,
    )


def close_pr(pr: PullRequest) -> None:
    """
    Closes a PR.
    """
    execute_gh_command(f"pr close {pr.url}", return_response=False)


def format_message(pr: PullRequest):
    return f"[bold]{pr.repository}[/bold]:{pr.labels_str} '{pr.title}' {pr.url}{pr.checks_str}"


async def main() -> None:
    terminal = Console()
    with terminal.status("Fetching PRs..."):
        prs = await get_pending_dependabot_prs()
    terminal.print(f"Found [red]{len(prs)}[/red] pending dependabot PRs to review")
    for pr in prs:
        terminal.print(format_message(pr))
        terminal.print(
            "Approve? ([bold]y[/bold]es/[bold]c[/bold]lose/[bold]N[/bold]o) ",
            end="",
        )
        option = terminal.input().lower().strip()
        if option in ["y", "yes"]:
            with terminal.status("Approving..."):
                approve_pr(pr)
                terminal.print("[green][bold]Approved[/]")
        elif option in ["c", "close"]:
            with terminal.status("Closing..."):
                close_pr(pr)
                terminal.print("[red][bold]Closed[/]")
        else:
            terminal.print("[yellow]Skipped[/yellow]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted")
        exit(0)
