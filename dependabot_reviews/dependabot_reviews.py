import asyncio
import json
import subprocess
import webbrowser
from textwrap import dedent

from furl import furl
from rich.console import Console


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
        status_checks = execute_gh_command(
            f"pr view {self.url} --json statusCheckRollup"
        )["statusCheckRollup"]

        if status_checks == []:
            return "[yellow] Checks not found[/yellow]"
        for check in status_checks:
            if check["conclusion"] != "SUCCESS":
                return "[red]Checks not passed[/red]"
            else:
                return "[green]Checks passed[/green]"

    def approve(self) -> None:
        """
        Approves the PR with the message "@dependabot merge".
        """
        execute_gh_command(
            f"pr review {self.url} --approve --body '@dependabot merge'",
            return_response=False,
        )

    def close(self) -> None:
        """
        Closes the PR without merging.
        """
        execute_gh_command(f"pr close {self.url}", return_response=False)


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
        *[
            asyncio.to_thread(
                PullRequest,
                pr["repository"]["nameWithOwner"],
                pr["title"],
                pr["url"],
                pr["labels"],
            )
            for pr in response
        ]
    )


async def main() -> None:
    terminal = Console()
    with terminal.status("Fetching PRs..."):
        prs = await get_pending_dependabot_prs()
    count = f"[red]{len(prs)}[/red]" if prs else "[green]0[/green]"
    terminal.print(f"Found {count} pending dependabot PRs to review")
    for pr in prs:
        terminal.print(pr)
        while True:
            terminal.print(
                "Approve? ([bold]y[/]es/[bold]c[/]lose/[bold]o[/]pen in browser/[bold]N[/]o) ",
                end="",
            )
            option = terminal.input().lower().strip()
            if option in ["y", "yes"]:
                with terminal.status("Approving..."):
                    pr.approve()
                    terminal.print("[green][bold]Approved[/]")
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
