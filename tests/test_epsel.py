import logging
import subprocess
import unittest.mock as mock
from io import StringIO
from pathlib import Path

import pytest

import epsel


def test_on_first_time():
    history = []

    def intro():
        history.append("hello world")

    @epsel.on_first_time(intro)
    def process(x):
        history.append(x)

    for x in range(5):
        process(x)

    assert history == ["hello world", 0, 1, 2, 3, 4]


def test_ensure_basic_logging_no_params():
    with mock.patch('logging.basicConfig') as basicConfig:
        @epsel.ensure_basic_logging
        def process(x):
            return x * 2

        basicConfig.assert_not_called()
        process(1)
        basicConfig.assert_called_once_with()
        process(2)
        basicConfig.assert_called_once_with()
        process(3)
        basicConfig.assert_called_once_with()


def test_ensure_basic_logging_params():
    with mock.patch('logging.basicConfig') as basicConfig:
        fmt = "%(message)s"
        lvl = logging.INFO

        @epsel.ensure_basic_logging(level=lvl, format=fmt)
        def process(x):
            return x * 2

        basicConfig.assert_not_called()
        process(1)
        basicConfig.assert_called_once_with(level=lvl, format=fmt)
        process(2)
        basicConfig.assert_called_once_with(level=lvl, format=fmt)


def test_ensure_basic_logging_output():
    with mock.patch(
            'logging.root', new=logging.RootLogger(level=logging.INFO)
    ) as root:
        # Root handlers must be empty for basicConfig to do anything
        assert logging.root.handlers == []

        buffer = StringIO()
        fmt = "%(levelname)s:%(name)s:%(message)s"

        @epsel.ensure_basic_logging(level=logging.INFO, format=fmt,
                                    stream=buffer)
        def process(x):
            root.info("Got {x!r}".format(x=x))
            return x * 2

        assert buffer.getvalue() == ""
        process(1)
        assert buffer.getvalue() == "INFO:root:Got 1\n"
        process(2)
        assert buffer.getvalue() == "INFO:root:Got 1\nINFO:root:Got 2\n"
        process(3)
        assert buffer.getvalue() == "INFO:root:Got 1\nINFO:root:Got 2\nINFO:root:Got 3\n"


@pytest.mark.parametrize("workers", [1, 2, 4])
def test_job_print_hello(workers):
    job_path = Path(__file__).parent / "job_print_hello.py"
    result = subprocess.run(
        [
            "spark-submit",
            "--master=local[{w}]".format(w=workers),
            str(job_path)
        ],
        capture_output=True, timeout=60, check=True
    )
    assert result.stderr.count(b"Hello world!") == workers
    assert result.stdout.startswith(b"[0, 1, 4, 9 16, 25")


def test_job_log_process():
    job_path = Path(__file__).parent / "job_log_process.py"
    res = subprocess.run(
        ["spark-submit", "--master=local[2]", str(job_path)],
        capture_output=True, timeout=60, check=True
    )
    logs = set(l for l in res.stderr.split(b"\n") if l.startswith(b"___"))
    assert logs == {
        b"___ job_log_process INFO Processing 0",
        b"___ job_log_process INFO Processing 1",
        b"___ job_log_process INFO Processing 2",
        b"___ job_log_process INFO Processing 3",
        b"___ job_log_process INFO Processing 4",
    }
    assert res.stdout == b"___ job_log_process INFO Result: [0, 1, 4, 9, 16]\n"