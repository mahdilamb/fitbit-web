"""Constants to be used by the api builder."""
from types import MappingProxyType
from typing import Any, Mapping

import builder.api

API_JSON = (
    "https://dev.fitbit.com/build/reference/web-api/explore/fitbit-web-api-swagger.json"
)
API_SHA256_HASH = "2bd9c196390f0e8fe11a05cb2ce8dfd736d8d9ce9e87f85d25477a8594ead719"

PERIODS = "1d", "7d", "30d", "1w", "1m", "3m", "6m", "1y", "max"


def parameters(method: builder.api.Method, path, *add) -> tuple[str | int, ...]:
    """Create the address to parameters from a path."""
    return (
        "paths",
        path,
        method,
        "parameters",
        *add,
    )


OVERRIDES: Mapping[tuple[str | int, ...], Any | None] = MappingProxyType(
    {
        parameters(
            "get",
            "/1/user/-/activities/active-zone-minutes/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            2,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/active-zone-minutes/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            3,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters(
            "get",
            "/1/user/-/activities/active-zone-minutes/date/{start-date}/{end-date}/time/{start-time}/{end-time}.json",
            3,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/active-zone-minutes/date/{start-date}/{end-date}/time/{start-time}/{end-time}.json",
            4,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/tracker/{resource-path}/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters(
            "get",
            "/1/user/-/activities/tracker/{resource-path}/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{base-date}/{end-date}/{detail-level}.json",
            3,
            "enum",
        ): ("1min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/1d/{detail-level}.json",
            2,
            "enum",
        ): ("1min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/{end-date}/{detail-level}/time/{start-time}/{end-time}.json",
            3,
            "enum",
        ): ("1min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/{end-date}/{detail-level}/time/{start-time}/{end-time}.json",
            4,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/{end-date}/{detail-level}/time/{start-time}/{end-time}.json",
            5,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            2,
            "enum",
        ): ("1min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            3,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/{resource-path}/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            4,
            "format",
        ): "time",
        parameters("get", "/1/user/-/activities/list.json", 0, "format"): (
            "date",
            "timestamp",
        ),
        parameters("get", "/1/user/-/activities/list.json", 1, "format"): (
            "date",
            "timestamp",
        ),
        parameters("get", "/1/user/-/activities/list.json", 2, "enum"): ("asc", "desc"),
        parameters("get", "/1/user/-/activities/goals/{period}.json", -1, "enum"): (
            "daily",
            "weekly",
        ),
        parameters(
            "get",
            "/1/user/-/body/log/fat/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters("get", "/1/user/-/body/log/{goal-type}/goal.json", 0, "enum"): (
            "weight",
            "fat",
        ),
        parameters(
            "get",
            "/1/user/-/body/log/weight/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters(
            "get",
            "/1/user/-/body/{resource-path}/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters("get", "/1/user/-/ecg/list.json", 0, "format"): (
            "date",
            "timestamp",
        ),
        parameters("get", "/1/user/-/ecg/list.json", 1, "format"): (
            "date",
            "timestamp",
        ),
        parameters("get", "/1/user/-/ecg/list.json", 2, "enum"): (
            "asc",
            "desc",
        ),
        parameters(
            "get", "/1/user/-/activities/heart/date/{date}/{period}.json", -1, "enum"
        ): PERIODS[:5],
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{base-date}/{end-date}.json",
            0,
            "format",
        ): "date",
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{base-date}/{end-date}.json",
            1,
            "format",
        ): "date",
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/{end-date}/{detail-level}.json",
            2,
            "enum",
        ): ("1sec", "1min", "5min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/{end-date}/{detail-level}/time/{start-time}/{end-time}.json",
            2,
            "enum",
        ): ("1sec", "1min", "5min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/{end-date}/{detail-level}/time/{start-time}/{end-time}.json",
            3,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/{end-date}/{detail-level}/time/{start-time}/{end-time}.json",
            4,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/1d/{detail-level}.json",
            1,
            "enum",
        ): ("1sec", "1min", "5min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            1,
            "enum",
        ): ("1sec", "1min", "5min", "15min"),
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            2,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/activities/heart/date/{date}/1d/{detail-level}/time/{start-time}/{end-time}.json",
            3,
            "format",
        ): "time",
        parameters(
            "get",
            "/1/user/-/foods/log/{resource-path}/date/{date}/{period}.json",
            -1,
            "enum",
        ): PERIODS,
        parameters("get", "/1.2/user/-/sleep/list.json", 0, "format"): (
            "date",
            "timestamp",
        ),
        parameters("get", "/1.2/user/-/sleep/list.json", 1, "format"): (
            "date",
            "timestamp",
        ),
        parameters("get", "/1.2/user/-/sleep/list.json", 2, "enum"): (
            "asc",
            "desc",
        ),
    }
)
