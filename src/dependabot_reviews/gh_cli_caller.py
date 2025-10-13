from subprocess import CompletedProcess, run


def execute_gh_command(command: str) -> CompletedProcess:
    """
    Execute a Github CLI command and return the JSON output.

    Raises CalledProcessError in the event of a non-zero return code.
    """

    return run(
        f"gh {command}",
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )
