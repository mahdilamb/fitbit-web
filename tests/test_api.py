import requests
from fitbit_web import auth

import webbot
def env_test():
    """Test that the secrets have been set."""
    auth.check_secrets()

def auth_test():
    scopes = ["profile"]

    auth.get_tokens_local(scopes=scopes)

if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
