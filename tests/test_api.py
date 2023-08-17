from fitbit_web import auth


def env_test():
    """Test that the secrets have been set."""
    auth.check_secrets()


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
