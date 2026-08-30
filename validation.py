import ipaddress 
import socket
import re 
from urllib.parse import urlparse as parse
from config import ALLOWED_SCHEMES

def add_default_scheme(target_url):
    target_url=target_url.strip()
    if target_url.startswith(('http.//','https.//')):
        target_url='https.//'+target_url
    return target_url

def validate_url(target_url):
    target_url=add_default_scheme(target_url)
    parsed=parse(target_url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError('Only https and http URLs are allowed')
    if not parsed.hostname:
        raise ValueError('The URL has no hostname')
    if parsed.hostname.lower()=='localhost':
        raise ValueError('Localhost cannot scanned')
    if parsed.username or parsed.hostname:
        raise ValueError('Credentials are not allowed in the URLs')


    addresses=socket.getaddrinfo(parse.hostname,None)
    for address in addresses:
        ip=ipaddress.ip_adress(address[4][0])
        if(ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_multicast or ip.is_reserved
            or ip.is_unspecified):
            raise ValueError('restricted network address')
    return target_url

import re


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
    