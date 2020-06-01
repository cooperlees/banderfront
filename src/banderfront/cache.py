#!/usr/bin/env python3

import asyncio
import aioredis
import logging
from packaging.utils import canonicalize_name
from typing import Any, Tuple


LOG = logging.getLogger(__name__)


class CacheMiss(ValueError):
    pass


class BanderCache:
    encoding = "utf-8"
    serial_key = "mirror-serial"
    index_key = "simple_index_root-html"
    index_serial_key = "simple_index_root_html-serial"

    def canon_key_names(self) -> Tuple[str, str]:
        canon_name = canonicalize_name(package_name)
        return (f"{canon_name}-html", f"{canon_name}-serial")

    async def get_package_simple_index(self, package_name: str) -> str:
        NotImplementedError("Implement in specific class")

    async def get_simple_index(self) -> str:
        NotImplementedError("Implement in specific class")

    async def update_package_simple_index(self, package_name: str) -> None:
        NotImplementedError("Implement in specific class")

    async def update_simple_index(self) -> None:
        NotImplementedError("Implement in specific class")


class RedisBanderCache(BanderCache):
    async def __aenter__(self, hostname: str = "localhost") -> Any:
        self.pool = await aioredis.create_redis_pool(f"redis://{hostname}")
        return self

    async def __aexit__(self, *exc: Any) -> None:
        self.pool.close()
        await self.pool.wait_closed()

    async def get_package_simple_index(self, package_name: str) -> str:
        package_html_key, package_serial_key = canon_key_names(package_name)
        serial = await self.pool.get(package_serial_key, encoding=self.encoding)
        if serial is None:
            raise CacheMiss("No serial - need to generate HTML")

        global_serial = await self.pool.get(self.serial_key, encoding=self.encoding)
        if int(global_serial) > int(serial):
            raise CacheMiss("Index is out of date")

        html = await self.pool.get(package_html_key, encoding=self.encoding)
        if not html:
            raise CacheMiss("HTML is invalid - Regenerate")

        return html

    async def get_simple_index(self) -> str:
        html = await self.pool.get(self.index_key, encoding=self.encoding)
        if not html:
            raise CacheMiss("Global Index HTML is invalid - Regenerate")

        return html

    async def update_package_simple_index(self, package_name: str, html: str, serial: str) -> None:
        package_html_key, package_serial_key = canon_key_names(package_name)
        LOG.info(f"Updating Simple Index html for {package_html_key} serial {serial}")
        await asyncio.gather(
            self.pool.set(package_html_key, html), self.pool.set(package_serial_key, serial)
        )

    async def update_simple_index(self, html: str, serial: str) -> None:
        LOG.info(f"Updating Root Simple Index html for serial {serial}")
        await asyncio.gather(
            self.pool.set(self.index_key, html), self.pool.set(self.index_serial_key, serial)
        )


async def test_redis() -> int:
    ci_test_html = "<html><head><title>Testing</title></head></html>"
    ci_test_serial = "69"

    async with RedisBanderCache() as rbc:
        before_serial = None
        try:
            before_serial = await rbc.get_simple_index()
            print("No cache miss ... wtf?")
        except CacheMiss as cm:
            print(f"Before Serial: {before_serial} - {cm}")

        await rbc.update_simple_index(ci_test_html, ci_test_serial)

        after_html = await rbc.get_simple_index()
        print(after_html)


if __name__ == "__main__":
    asyncio.run(test_redis())
