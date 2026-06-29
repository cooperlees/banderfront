#!/usr/bin/env python3

import logging

from aiohttp import web


LOG = logging.getLogger(__name__)


async def package_download(
    request: web.Request,
) -> web.FileResponse | web.Response | web.StreamResponse:
    package_path = request.match_info["url_path"]
    return web.Response(
        text=(
            "🔜 Package downloads coming soon ... Not smart enough to "
            + f"find {package_path} yet!\n"
        )
    )


async def simple_package_root(request: web.Request) -> web.Response:
    package_name = request.match_info["package_name"]
    return web.Response(text=f"Simple {package_name} Index\n")


async def simple_root(request: web.Request) -> web.Response:
    return web.Response(text="Simple Index\n")
