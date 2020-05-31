#!/usr/bin/env python3
# Copyright (c) 2014-present, Facebook, Inc.

import asyncio
import logging
from os import environ

from aiohttp import web


LOG = logging.getLogger(__name__)
ROOT_ASCII = r"""
 ____                     _                                 _          _        ____          ____   ___    __  __  _
| __ )   __ _  _ __    __| |  ___  _ __  ___  _ __    __ _ | |_   ___ | |__    |  _ \  _   _ |  _ \ |_ _|  |  \/  |(_) _ __  _ __   ___   _ __
|  _ \  / _` || '_ \  / _` | / _ \| '__|/ __|| '_ \  / _` || __| / __|| '_ \   | |_) || | | || |_) | | |   | |\/| || || '__|| '__| / _ \ | '__|
| |_) || (_| || | | || (_| ||  __/| |   \__ \| | | || (_| || |_ | (__ | | | |  |  __/ | |_| ||  __/  | |   | |  | || || |   | |   | (_) || |
|____/  \__,_||_| |_| \__,_| \___||_|   |___/|_| |_| \__,_| \__| \___||_| |_|  |_|     \__, ||_|    |___|  |_|  |_||_||_|   |_|    \___/ |_|
                                                                                       |___/
"""
SIXTYNINE_ASCII = r""".------..------.
|6.--. ||9.--. |
| (\/) || :/\: |
| :\/: || (__) |
| '--'6|| '--'9|
`------'`------'
"""

async def index(request: web.Request) -> web.Response:
    return web.Response(text=ROOT_ASCII)


async def sixtynine(request: web.Request) -> web.Response:
    return web.Response(text=SIXTYNINE_ASCII)


async def serve() -> web.Application:
    log_level = logging.DEBUG if "DEBUG" in environ else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )
    LOG.info("Finished setting up logging for the software portal")

    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/69", sixtynine)
    app.router.add_get("/sixtynine", sixtynine)

    LOG.debug("Finished setting up routes")
    return app


if __name__ == "__main__":
    LOG.error("This module is designed to run via gunicorn")
