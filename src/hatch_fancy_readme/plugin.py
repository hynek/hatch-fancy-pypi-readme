# SPDX-FileCopyrightText: 2022-present Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from hatchling.metadata.plugin.interface import MetadataHookInterface


class FancyReadmeMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = "fancy_readme"

    def update(self, metadata: dict) -> None:
        """
        Update the project table's metadata.
        """
        XXX
