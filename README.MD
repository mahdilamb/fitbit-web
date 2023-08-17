# Fitbit WebAPI

Python module for accessing Fitbit WebAPI. Currently only supports sync and get methods.

## Installation

You can either install for development using:

```shell
python -m pip install -e .[all]
```

Add to `pyproject.toml`:

```toml
[project]
name = "..."

dependencies = [
    "fitbit-web@git+https://github.com/mahdilamb/fitbit-web"
]
```

# Usage

To use fitbit, ensure you have a [developer account](https://dev.fitbit.com/build/reference/web-api/developer-guide/getting-started/) and have created an App using the Personal token.

Ensure that you have set the following environment variables:

* `FITBIT_CLIENT_ID`
* `FITBIT_CLIENT_SECRET`
* `FITBIT_REDIRECT_URL`

Alternatively, create a `.env` file as follows:

```.env
FITBIT_CLIENT_ID=<client-id>
FITBIT_CLIENT_SECRET=<client-secret>
FITBIT_REDIRECT_URL=<redirect-url>

```

```python
from fitbit_web import client, auth


web_client = client.Client(auth.get_tokens_local(scopes=["profile"]))
print(web_client.get_profile())
```

Or for the async version:

```python
from fitbit_web import client, auth
import asyncio


async def main():
    async with client.Client(
        auth.get_tokens_local(scopes=["profile"])
    ).async_client() as async_client:
        print(await async_client.aget_profile())


if __name__ == "__main__":
    asyncio.run(main())

```

## Development

The client is generated using the `builder` package. This can either be run using `make`:

```shell
make api
```

or running the command:

```shell
python -m builder
```

Please ensure you have install using the `[all]` optional group.

### Notes

For the sake of having good type hints, there are some extra types (e.g. `timestamp`) and some of the original API is modified so that the parameters match the description (e.g. using enums where possible). The *overrides* are present in [builder/constants.py::OVERRIDES](builder/constants.py). To ensure that developers are alerted to changes in the API, the current SHA256 must be supplied in constants as `API_SHA256_HASH`.
