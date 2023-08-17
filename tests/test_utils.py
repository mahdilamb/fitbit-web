import pytest

from fitbit_web import utils


def test_format(fn, sample: str, exception: type[Exception] | None):
    if exception is not None:
        with pytest.raises(exception):
            fn(sample)
        return
    fn(sample)


@pytest.mark.parametrize(
    ("sample", "exception"),
    [("23:04", None), ("43:04", ValueError), ("23-04", ValueError)],
)
def time_test(sample: str, exception: type[Exception] | None):
    test_format(utils.format_time, sample, exception)


@pytest.mark.parametrize(
    ("sample", "exception"),
    [("02-04-02", ValueError), ("2020-03-04", None), ("today", None)],
)
def date_test(sample: str, exception: type[Exception] | None):
    test_format(utils.format_date, sample, exception)


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
