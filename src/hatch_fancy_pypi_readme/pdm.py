# SPDX-FileCopyrightText: 2023 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._builder import build_text
from ._config import load_and_validate_config


if TYPE_CHECKING:
    from pdm.backend.hooks import Context


class FancyReadmeHook:
    # Should be under "tool.pdm.build.hooks.fancy-pypi-readme" when
    # running under pdm-backend?
    CONFIG_KEY = "tool.hatch.metadata.hooks.fancy-pypi-readme"

    def pdm_build_hook_enabled(self, context: Context) -> bool:
        metadata = context.config.metadata
        if "readme" not in metadata.get("dynamic", []):
            return False
        return self._have_config(context)

    def pdm_build_initialize(self, context: Context) -> None:
        metadata = context.config.metadata
        config = load_and_validate_config(self._get_config(context))

        metadata.get("dynamic", []).remove("readme")
        metadata["readme"] = {
            "content-type": config.content_type,
            "text": build_text(config.fragments, config.substitutions),
        }

    def _have_config(self, context: Context) -> bool:
        try:
            self._get_config(context)
        except (KeyError, TypeError):
            return False
        return True

    def _get_config(self, context: Context) -> dict[str, Any]:
        data = context.config.data
        for key in self.CONFIG_KEY.split("."):
            data = data[key]
        if not isinstance(data, dict):
            msg = f"expected a dict at `{self.CONFIG_KEY}`"
            raise TypeError(msg)
        return data
