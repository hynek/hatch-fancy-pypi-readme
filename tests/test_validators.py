# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import pytest

from jsonschema import ValidationError

from hatch_fancy_pypi_readme._validators import CustomValidator, is_regex


validator = CustomValidator({"type": "string", "regex": True})
validator_false = CustomValidator({"type": "string", "regex": False})


class TestIsRegexValidator:
    def test_ok_true(self):
        """
        A valid regex passes.
        """
        validator.validate(".+")

    def test_fail_true(self):
        """
        An invalid regex fails.
        """
        with pytest.raises(ValidationError) as ei:
            validator.validate("???")

        assert (
            "'???' is not a valid Python regular expression"
            == ei.value.message
        )

    def test_ok_false(self):
        """
        If a string must not be valid regex and it isn't, it passes.

        No, I don't know when this could ever be useful.
        """
        validator_false.validate("???")

    def test_fail_false(self):
        """
        If a string must not be valid regex and it is, it fails.

        No, I don't know when this could ever be useful.
        """
        with pytest.raises(ValidationError) as ei:
            validator_false.validate(".+")

        assert "'.+' is a valid Python regular expression" == ei.value.message

    @pytest.mark.parametrize("v", [validator, validator_false])
    def test_not_a_string(self, v):
        """
        Non-strings are not regexes, but also not strings that aren't regexes.
        """
        with pytest.raises(ValidationError) as ei:
            v.validate(42)

        assert "42 is not of type 'string'" == ei.value.message

    def test_not_a_string_direct(self):
        """
        The order in that the validators run is not guaranteed, so check we
        can handle getting a non-string passed.
        """
        assert () == tuple(is_regex(validator, True, 42, None))
