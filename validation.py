import ipaddress
import socket
import re
from urllib.parse import urlparse
from config import ALLOWED_SCHEMES

def add_default_scheme(target_url):
    target_url = target_url.strip()
    if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url
    return target_url

def validate_url(target_url):
    target_url = add_default_scheme(target_url)
    parsed = urlparse(target_url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    if not parsed.hostname:
        raise ValueError("The URL has no hostname")
    if parsed.hostname.lower() == "localhost":
        raise ValueError("Localhost cannot be scanned")
    if parsed.username or parsed.password:
        raise ValueError("Credentials in URLs are not allowed")
    return target_url


def safe_username(username: str) -> str:
    username = username.strip().lower()

    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        username,
    ).strip("_")

    if not safe_name:
        raise ValueError("Invalid username")

    return safe_name[:50]
