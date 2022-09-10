# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

"""
This defines our CustomValidator that uses the correct draft and adds custom
validators.
"""

from __future__ import annotations

import re

from typing import Any, Generator

import jsonschema


def is_regex(
    validator: jsonschema.validators.Draft202012Validator,
    regex: bool,  # value from schema
    instance: Any,
    schema: jsonschema.Schema,
) -> Generator[jsonschema.ValidationError, None, None]:
    """
    If *regex* is True, ensure *instance* is a valid regular expression. If
    it's False, ensure it's NOT valid.
    """
    if not validator.is_type(instance, "string"):
        return

    try:
        re.compile(instance)
    except (re.error, ValueError):
        if regex:
            yield jsonschema.ValidationError(
                f"'{instance}' is not a valid Python regular expression"
            )
    else:
        if not regex:
            yield jsonschema.ValidationError(
                f"'{instance}' is a valid Python regular expression"
            )


CustomValidator = jsonschema.validators.extend(
    jsonschema.validators.Draft202012Validator, validators={"regex": is_regex}
)
