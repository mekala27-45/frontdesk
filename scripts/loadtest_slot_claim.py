"""Run the real Postgres HTTP race test, with mandatory dependency probing."""

import shutil
import subprocess
import sys

if __name__ == "__main__":
    if (
        not shutil.which("docker")
        or subprocess.run(["docker", "info"], capture_output=True).returncode
    ):
        raise SystemExit("Docker daemon required for the Postgres concurrency benchmark.")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_scheduling.py::test_fifty_concurrent_claims",
            "-q",
            "-s",
        ],
        check=True,
    )
