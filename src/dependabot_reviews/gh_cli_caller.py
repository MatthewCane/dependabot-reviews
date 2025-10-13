import json
from subprocess import CalledProcessError, CompletedProcess, run


def execute_gh_command(command: str) -> CompletedProcess:
    """
    Execute a Github CLI command and return the JSON output.
    """
    try:
        result = run(
            f"gh {command}",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        return result

    except CalledProcessError as e:
        error_message = f"Command failed with exit code {e.returncode}\n"
        error_message += f"stdout: {e.stdout}\n"
        error_message += f"stderr: {e.stderr}"
        raise RuntimeError(error_message) from e

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON output: {e}\nOutput: {result.stdout}"
        ) from e
