# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Iterable, Tuple, Union

from jsonschema.exceptions import ValidationError


PathElement = Union[int, str]
FieldPath = Tuple[PathElement, ...]


def errors_to_human_strings(
    excs: Iterable[ValidationError], extra_path: FieldPath = ()
) -> list[str]:
    """
    Make *excs* as human-readable as possible.

    Add *extra_path* between base path and the error's path (which is
    incomplete from the user's view).
    """
    errs = []

    for e in excs:
        full_path = BASE_PATH + extra_path + tuple(e.path)
        errs.append(_VALIDATOR_TO_FORMATTER[e.validator](full_path, e))

    return errs


BASE_PATH = ("tool.hatch", "metadata", "hooks", "fancy-pypi-readme")


def _format_missing(path: FieldPath, e: ValidationError) -> str:
    missing = e.message[1:].split("'", 1)[0]

    return f"{_dot_path(path, missing)} is missing."


def _format_not_enough(path: FieldPath, e: ValidationError) -> str:
    assert e.validator_value == 1

    return f"{_dot_path(path)} must not be empty."


def _format_additional_fields(path: FieldPath, e: ValidationError) -> str:
    extra = e.message.split("'")[-2]
    return f"{_dot_path(path, extra)}: extra field not permitted."


def _format_wrong_type(path: FieldPath, e: ValidationError) -> str:
    return f"{_dot_path(path)} is of wrong type: {e.message}"


def _format_path_w_message(path: FieldPath, e: ValidationError) -> str:
    return f"{_dot_path(path)}: {e.message}"


def _dot_path(path: FieldPath, last: str | None = None) -> str:
    """
    Concat our base path with `e.absolute_path` and append *last* if specified.
    """
    common = ".".join(str(p) for p in path)

    if not last:
        return common

    # We end up with two dots if there's no path.
    maybe_dot = "." if path else ""

    return f"{common}{maybe_dot}{last}"


_VALIDATOR_TO_FORMATTER = {
    "required": _format_missing,
    "type": _format_wrong_type,
    "minItems": _format_not_enough,
    "minLength": _format_not_enough,
    "additionalProperties": _format_additional_fields,
    "format": _format_path_w_message,
    "enum": _format_path_w_message,
    "regex": _format_path_w_message,
}
