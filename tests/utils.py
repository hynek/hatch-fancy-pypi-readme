# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import subprocess
import sys
from functools import reduce

import pytest


def run(*args, check=True):
    process = subprocess.run(  # noqa: PLW1510
        [sys.executable, "-m", *args],  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
    )
    if check and process.returncode:
        pytest.fail(process.stdout)

    return process.stdout


def append(file, text):
    file.write_text(file.read_text() + text)


def replace(file, subs):
    file.write_text(
        reduce(lambda acc, x: acc.replace(*x), subs.items(), file.read_text())
    )
