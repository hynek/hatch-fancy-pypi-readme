# SPDX-FileCopyrightText: 2022-present Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from hatchling.plugin import hookimpl

from .plugin import  FancyReadmeMetadataHook


@hookimpl
def hatch_register_metadata_hook() -> type[MetadataHookInterface]:
    XXX
    return FancyReadmeMetadataHook
