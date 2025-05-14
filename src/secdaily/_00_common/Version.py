"""
Version management module for checking package updates. Provides functions to check for newer versions
of the package on PyPI and display update notifications to users.
"""

import requests
from packaging import version

import secdaily


def get_latest_pypi_version():
    url = "https://pypi.org/pypi/secdaily/json"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data["info"]["version"]
    return ""


def is_newer_version_available():
    pypi_version = get_latest_pypi_version()
    if pypi_version == "":
        return False

    current_version = secdaily.__version__

    return version.parse(pypi_version) > version.parse(current_version)


def print_newer_version_message():
    """printed if a newer version of the library is available"""

    if not is_newer_version_available():
        return

    print("\n\n")
    print(
        f"    A newer version of secfsdstools ({get_latest_pypi_version()}) is available on pypi.org."
        " Please consider upgrading."
    )
    print("\n\n")


if __name__ == "__main__":
    print(get_latest_pypi_version())
    print(secdaily.__version__)
    print(is_newer_version_available())
