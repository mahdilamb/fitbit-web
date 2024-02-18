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
from typing import Literal, Sequence, cast

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


AUTH_URL = "https://www.fitbit.com/oauth2/authorize?response_type=code&code_challenge_method=S256"
TOKEN_URL = "https://api.fitbit.com/oauth2/token?grant_type=authorization_code"
REFRESH_URL = "https://api.fitbit.com/oauth2/token?grant_type=refresh_token"

CODE_VERIFIER = secrets.token_urlsafe(96)


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
            f"{REFRESH_URL}client_id={CLIENT_ID}&refresh_token={self.refresh_token}",
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


def code_challenge(code_verifier: str = CODE_VERIFIER) -> str:
    """Hash the code verifier."""
    return (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
    )


def get_authorization_url(
    scopes: Sequence[Scope] = typing.get_args(Scope), code_verifier: str = CODE_VERIFIER
):
    """Get the OAuth2 url."""
    check_secrets()

    return f"{AUTH_URL}&client_id={CLIENT_ID}&code_challenge={code_challenge(code_verifier)}&scope={('+'.join(scopes))}&redirect_uri={urllib.parse.quote(REDIRECT_URL)}"


def get_token_url(code: str, code_verifier: str = CODE_VERIFIER):
    """Get the token url."""
    return f"{TOKEN_URL}&client_id={CLIENT_ID}&code={code}&code_verifier={code_verifier}&redirect_uri={urllib.parse.quote(REDIRECT_URL)}"


def token_from_code(code: str, code_verifier: str = CODE_VERIFIER) -> AuthTokens:
    """Get a token from the code returned from the authorization process.

    Note that the code_verified must be hashed as in the original process.
    """
    response = requests.post(
        get_token_url(code, code_verifier=code_verifier),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64.urlsafe_b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')}",
            "Accept": "application/json",
        },
        timeout=2.0,
    ).json()
    response["scope"] = tuple(w.strip() for w in response["scope"].split())

    return AuthTokens(**response)


def get_tokens_local(
    scopes: Sequence[Scope] = typing.get_args(Scope),
    auto_open: bool = True,
    code_verifier: str = CODE_VERIFIER,
) -> AuthTokens:
    """Get the auth token using the secrets in the constants.

    Parameters
    ----------
    scopes : Sequence[Scope], optional
        The scopes to use for authorization, by default all
    auto_open : bool, optional
        Whether to open a browser windows, by default True

    Returns
    -------
    AuthTokens
        The authorization token.

    Raises
    ------
    RuntimeError
        If redirect is not to localhost.
    """
    check_secrets()
    oauth2_url = get_authorization_url(scopes, code_verifier=code_verifier)
    if auto_open:
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
                        """<html>
    <head>
        
    </head>
    <body>You can now close this tab...
        <script type='text/javascript'>
                window.opener && window.opener.location.reload(true);
                window.close();
        </script>
    </body>
</html>""",
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
    return token_from_code(cast(str, code), code_verifier=code_verifier)
