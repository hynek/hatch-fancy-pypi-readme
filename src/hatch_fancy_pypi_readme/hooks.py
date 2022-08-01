# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl

from ._builder import build_text
from ._config import load_and_validate_config


class FancyReadmeMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = "fancy-pypi-readme"

    def update(self, metadata: dict[str, Any]) -> None:
        """
        Update the project table's metadata.
        """

        config = load_and_validate_config(self.config)

        metadata["readme"] = {
            "content-type": config.content_type,
            "text": build_text(config.fragments),
        }


@hookimpl  # type: ignore
def hatch_register_metadata_hook() -> type[MetadataHookInterface]:
    return FancyReadmeMetadataHook
