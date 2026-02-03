"""Credential management using system keychain.

macOS: Uses `security` command (Keychain)
Linux: Uses `secret-tool` (libsecret)
"""

import subprocess
import sys
from dataclasses import dataclass


SERVICE_NAME = "freshrss-skill"
KEYS = ["api_url", "username", "password"]


@dataclass
class Credentials:
    """FreshRSS API credentials."""

    api_url: str
    username: str
    password: str


def _is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def _is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def _run_command(cmd: list[str], input_data: str | None = None) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


# =============================================================================
# macOS Keychain
# =============================================================================


def _macos_set(key: str, value: str) -> bool:
    """Store a value in macOS Keychain."""
    # Delete existing entry first (ignore errors if not found)
    _run_command([
        "security", "delete-generic-password",
        "-s", SERVICE_NAME,
        "-a", key,
    ])
    # Add new entry
    code, _, _ = _run_command([
        "security", "add-generic-password",
        "-s", SERVICE_NAME,
        "-a", key,
        "-w", value,
    ])
    return code == 0


def _macos_get(key: str) -> str | None:
    """Retrieve a value from macOS Keychain."""
    code, stdout, _ = _run_command([
        "security", "find-generic-password",
        "-s", SERVICE_NAME,
        "-a", key,
        "-w",
    ])
    if code == 0:
        return stdout.strip()
    return None


def _macos_delete(key: str) -> bool:
    """Delete a value from macOS Keychain."""
    code, _, _ = _run_command([
        "security", "delete-generic-password",
        "-s", SERVICE_NAME,
        "-a", key,
    ])
    return code == 0


# =============================================================================
# Linux libsecret
# =============================================================================


def _linux_set(key: str, value: str) -> bool:
    """Store a value in Linux secret storage."""
    code, _, _ = _run_command(
        [
            "secret-tool", "store",
            "--label", f"{SERVICE_NAME}/{key}",
            "service", SERVICE_NAME,
            "key", key,
        ],
        input_data=value,
    )
    return code == 0


def _linux_get(key: str) -> str | None:
    """Retrieve a value from Linux secret storage."""
    code, stdout, _ = _run_command([
        "secret-tool", "lookup",
        "service", SERVICE_NAME,
        "key", key,
    ])
    if code == 0:
        return stdout.strip()
    return None


def _linux_delete(key: str) -> bool:
    """Delete a value from Linux secret storage."""
    code, _, _ = _run_command([
        "secret-tool", "clear",
        "service", SERVICE_NAME,
        "key", key,
    ])
    return code == 0


# =============================================================================
# Public API
# =============================================================================


def _set_value(key: str, value: str) -> bool:
    """Store a credential value."""
    if _is_macos():
        return _macos_set(key, value)
    elif _is_linux():
        return _linux_set(key, value)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def _get_value(key: str) -> str | None:
    """Retrieve a credential value."""
    if _is_macos():
        return _macos_get(key)
    elif _is_linux():
        return _linux_get(key)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def _delete_value(key: str) -> bool:
    """Delete a credential value."""
    if _is_macos():
        return _macos_delete(key)
    elif _is_linux():
        return _linux_delete(key)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def get_credentials() -> Credentials | None:
    """Get stored credentials from keychain.

    Returns:
        Credentials object if all values are found, None otherwise.
    """
    values = {}
    for key in KEYS:
        value = _get_value(key)
        if value is None:
            return None
        values[key] = value
    return Credentials(**values)


def setup_credentials(api_url: str, username: str, password: str) -> bool:
    """Store credentials in keychain.

    Args:
        api_url: FreshRSS API URL
        username: FreshRSS username
        password: FreshRSS API password

    Returns:
        True if all credentials were stored successfully.
    """
    success = True
    success = success and _set_value("api_url", api_url)
    success = success and _set_value("username", username)
    success = success and _set_value("password", password)
    return success


def clear_credentials() -> bool:
    """Clear all stored credentials.

    Returns:
        True if all credentials were cleared.
    """
    success = True
    for key in KEYS:
        success = success and _delete_value(key)
    return success
