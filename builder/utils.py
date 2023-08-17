"""Utility functions for building the api."""
import re


def camel_to_snake_case(camel_cased: str) -> str:
    """Convert camelCase to snake_case.

    Adapted from https://stackoverflow.com/a/1176023.
    """
    camel_cased = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", camel_cased)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", camel_cased).lower()
