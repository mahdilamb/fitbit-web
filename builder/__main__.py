"""Script for building an API from the swagger json schema of Fitbit Web API."""
import hashlib
from collections import defaultdict
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import requests

import builder.api
import builder.constants
import builder.utils
from fitbit_web import utils

DATE_ANNOTATION = str(next(iter(utils.format_date.__annotations__.values()))).replace(
    "typing.", ""
)
TIMESTAMP_ANNOTATION = str(
    next(iter(utils.format_timestamp.__annotations__.values()))
).replace("typing.", "")
TIME_ANNOTATION = str(next(iter(utils.format_time.__annotations__.values()))).replace(
    "typing.", ""
)

PYTYPES: Mapping[
    builder.api.ParameterType
    | builder.api.ParameterFormat
    | Sequence[builder.api.ParameterFormat],
    str,
] = MappingProxyType(
    {
        "boolean": "bool",
        "integer": "int",
        "string": "str",
        "date": DATE_ANNOTATION,
        "time": TIME_ANNOTATION,
        ("date", "timestamp"): f"{DATE_ANNOTATION} | str",
    }
)


def _print_dict(params: Sequence[builder.api.Parameters]):
    def wrap(
        param,
        type: builder.api.ParameterType | None,
        format: builder.api.ParameterFormat | None,
    ):
        if format == "date":
            return f"utils.{utils.format_date.__name__}({param})"
        elif format == "time":
            return f"utils.{utils.format_time.__name__}({param})"
        elif format == ("date", "timestamp"):
            return f"utils.{utils.format_date_or_timestamp.__name__}({param})"
        return f"{param}"

    return (
        "{"
        + (
            ", ".join(
                [
                    f"'{param.name}': {wrap(builder.utils.camel_to_snake_case(param.name.replace('-','_')),param.type,param.format)}"
                    for param in params
                ]
            )
        )
        + "}"
    )


def build(
    api: builder.api.FitbitWebAPI,
    utils_path: str,
    output_path: str | None = None,
    spacing: str = "\t",
):
    r"""Build the client API.

    Parameters
    ----------
    api : FitbitWebAPI
        The source API model.
    utils_path : str
        The path to the utils package as a python module (e.g. `fitbit_web.utils`)
    output_path : str | None, optional
        The output path, by default None
    spacing : str, optional
        The spacing to use, by default "\t"
    """

    def make_def(path: str, props: builder.api.Operation):
        endpoint = path
        output = (
            f"{spacing}def {builder.utils.camel_to_snake_case(props.operation_id)}(self"
        )
        path_kwargs = ""
        query_kwargs = ""
        params_docstring = ""
        if props.parameters:
            sorted_params = sorted(
                props.parameters,
                key=lambda val: val.default is not None or not val.required,
            )
            params: Mapping[
                builder.api.ParameterLocation, list[builder.api.Parameters]
            ] = defaultdict(list)

            for param in sorted_params:
                params[param.in_].append(param)
                type = PYTYPES[param.type]
                default = param.default
                if param.format is not None:
                    type = PYTYPES[param.format]
                if param.enum is not None:
                    type = f"Literal{list(param.enum)}"
                if default is not None and type not in ("int", "bool", DATE_ANNOTATION):
                    default = f"'{default}'"
                output += f", {builder.utils.camel_to_snake_case(param.name.replace('-','_'))}: {type}"
                params_docstring += f"{spacing*2}{builder.utils.camel_to_snake_case(param.name.replace('-','_'))} : {type}{', optional' if not param.required else ''}\n{spacing*3}{param.description}\n\n"

                if not param.required:
                    output += f" | None = {default if default is not None else 'None' }"
                elif default:
                    output += f" = {default}"

            if (path_params := params.get("path")) is not None:
                path_kwargs = ", param_kwargs=" + _print_dict(path_params)
            if (query_params := params.get("query")) is not None:
                query_kwargs = ", query_kwargs=" + _print_dict(query_params)

        output += "):\n"

        output += f'''{spacing*2}"""{(props.summary + """

""") if props.summary else ""}{(f"""{spacing*2}"""+props.description + """
""" if props.description else "")}{spacing*2}\n{spacing*2}Endpoint: '{endpoint}'\n{spacing*2}Scopes: {props.security[0].oauth2}'''
        if params_docstring:
            output += (
                f"\n\n{spacing*2}Parameters\n{spacing*2}----------\n{params_docstring}"
            )

        output += f'\n{spacing*2}"""\n'
        output += f"{spacing*2}return self._get('{path}'{path_kwargs}{query_kwargs})"

        return output

    output = f"""
\"\"\"Abstract implementations for the Fitbit Web API.\"\"\"
import abc
import datetime
from typing import Any, Literal, Annotated, Union
import {utils_path} as utils

class FitbitWebApi(abc.ABC):
{spacing}\"\"\"API containing the autogenerated methods for the Fitbit Web API.\"\"\"
{spacing}
{spacing}@abc.abstractmethod
{spacing}def _get(
{spacing*2}self,
{spacing*2}url: str,
{spacing*2}param_kwargs: dict[str, Any] | None = None,
{spacing*2}query_kwargs: dict[str, Any] | None = None,
{spacing}) -> dict[str, Any]:
{spacing*2}...
"""
    for path, path_properties in api.paths.items():
        if "get" not in path_properties:
            continue
        output += make_def(path, path_properties["get"]) + "\n"
    if output_path is not None:
        with open(output_path, "w") as fp:
            fp.write(output)
    return output


def apply_overrides(data: dict[tuple[str | int, ...], Any]):
    """Apply the overrides to data.

    Parameters
    ----------
    data : dict[tuple[str | int, ...], Any]
        The data to modify
    """

    def apply_override(path, override):
        node = data
        while len(path) > 1:
            el, *path = path
            node = node[el]
        if override is None:
            del node[path[0]]
        else:
            node[path[0]] = override

    for override in builder.constants.OVERRIDES.items():
        apply_override(*override)
    return data


def main():
    """Run the builder and format the output."""
    import black
    import isort.main

    import fitbit_web.api as client_api
    from fitbit_web import utils

    response = requests.get(builder.constants.API_JSON)

    response_hash = hashlib.sha256(response.content).hexdigest()
    if builder.constants.API_SHA256_HASH is None:
        raise RuntimeError(
            f"The variable `API_SHA256_HASH` has not been set. Ensure you are using the right API_JSON. The current hash is:\n{response_hash}"
        )
    if builder.constants.API_SHA256_HASH != response_hash:
        raise RuntimeError("The API has changed. Please re-check the repo.")
    api = builder.api.FitbitWebAPI.model_validate(apply_overrides(response.json()))

    build(api, output_path=client_api.__file__, utils_path=utils.__name__)
    isort.file(client_api.__file__)
    black.main([client_api.__file__])


main()
