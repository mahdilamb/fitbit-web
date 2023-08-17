"""Fitbit WebAPI authorization utilities."""
import base64
import dataclasses
import hashlib
import os
import secrets
import threading
import typing
import urllib.parse
import webbrowser
from http import server
from typing import Literal, Sequence

import requests
from dotenv import load_dotenv

try:
    from loguru import logger
except ModuleNotFoundError:
    import logging

    logger = logging.getLogger()
load_dotenv()

CLIENT_ID = os.getenv("FITBIT_CLIENT_ID", None)
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET", None)
REDIRECT_URL = os.getenv("FITBIT_REDIRECT_URL", None)

CODE_VERIFIER = secrets.token_urlsafe(96)
CODE_CHALLENGE: str = (
    base64.urlsafe_b64encode(hashlib.sha256(CODE_VERIFIER.encode("utf-8")).digest())
    .decode("utf-8")
    .rstrip("=")
)


Scope = Literal[
    "activity",
    "cardio_fitness",
    "electrocardiogram",
    "heartrate",
    "location",
    "nutrition",
    "oxygen_saturation",
    "profile",
    "respiratory_rate",
    "settings",
    "sleep",
    "social",
    "temperature",
    "weight",
]


@dataclasses.dataclass(frozen=True)
class AuthTokens:
    """Dataclass containing OAuth2 token details."""

    access_token: str
    expires_in: int
    refresh_token: str
    scope: tuple[Scope, ...]
    token_type: Literal["Bearer"]
    user_id: str

    def refresh(self) -> "AuthTokens":
        """Refresh the auth tokens."""
        response = requests.post(
            f"https://api.fitbit.com/oauth2/token?client_id={CLIENT_ID}&refresh_token={self.refresh_token}&grant_type=refresh_token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {base64.urlsafe_b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')}",
                "Accept": "application/json",
            },
            timeout=2.0,
        ).json()
        response["scope"] = tuple(w.strip() for w in response["scope"].split())

        return AuthTokens(**response)


def check_secrets():
    """Check that the CLIENT_ID, CLIENT_SECRET and REDIRECT_URL have been specified."""
    if None in (CLIENT_ID, CLIENT_SECRET, REDIRECT_URL):
        raise RuntimeError(
            "Please ensure `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URL` are set."
        )


def get_tokens_local(scopes: Sequence[Scope] = typing.get_args(Scope)) -> AuthTokens:
    """Get the auth token using the secrets in the constants."""
    check_secrets()
    oauth2_url = get_oauth2_url(scopes)
    webbrowser.open(oauth2_url)
    print(f"Authorize Fitbit usage: {oauth2_url}")
    if (host := urllib.parse.urlparse(REDIRECT_URL).netloc.split(":", maxsplit=1))[
        0
    ] not in ("localhost", "127.0.0.1"):
        raise RuntimeError(
            "Function only supports getting a token from the local connection."
        )
    address, port = host
    code = None

    class AuthClient(server.BaseHTTPRequestHandler):
        def do_GET(self):
            path = urllib.parse.urlsplit(self.path)
            if path.netloc not in ("/", ""):
                self.send_error(404)
                return
            try:
                nonlocal code
                code = urllib.parse.parse_qs(path.query)["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    bytes(
                        "<html><head><script type='text/javascript'>window.close()</script></head><body>You can now close this tab...</body></html>",
                        "utf-8",
                    )
                )
            except Exception as e:
                logger.exception(e)
                self.send_error(500)
            finally:
                server_closer = threading.Thread(
                    target=tmp_server.shutdown, daemon=True
                )
                server_closer.start()

    tmp_server = server.HTTPServer((address, int(port)), AuthClient)
    tmp_server.serve_forever()
    response = requests.post(
        f"https://api.fitbit.com/oauth2/token?client_id={CLIENT_ID}&code={code}&code_verifier={CODE_VERIFIER}&grant_type=authorization_code&redirect_uri={urllib.parse.quote(REDIRECT_URL)}",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64.urlsafe_b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')}",
            "Accept": "application/json",
        },
        timeout=2.0,
    ).json()
    response["scope"] = tuple(w.strip() for w in response["scope"].split())

    return AuthTokens(**response)


def get_oauth2_url(scopes: Sequence[Scope]):
    """Get the OAuth2 url."""
    check_secrets()

    return f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&code_challenge={CODE_CHALLENGE}&code_challenge_method=S256&scope={('+'.join(scopes))}&redirect_uri={urllib.parse.quote(REDIRECT_URL)}"
