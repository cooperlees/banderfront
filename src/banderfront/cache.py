#!/usr/bin/env python3

import asyncio
import logging
from abc import ABC, abstractmethod
from types import TracebackType
from typing import cast

import redis.asyncio as redis
from packaging.utils import canonicalize_name


LOG = logging.getLogger(__name__)


class CacheMiss(ValueError):
    pass


class BanderCache(ABC):
    encoding = "utf-8"
    serial_key = "mirror-serial"
    index_key = "simple_index_root-html"
    index_serial_key = "simple_index_root_html-serial"

    def canon_key_names(self, package_name: str) -> tuple[str, str]:
        canon_name = canonicalize_name(package_name)
        return (f"{canon_name}-html", f"{canon_name}-serial")

    @abstractmethod
    async def get_package_simple_index(self, package_name: str) -> str: ...

    @abstractmethod
    async def get_simple_index(self) -> str: ...

    @abstractmethod
    async def update_package_simple_index(
        self, package_name: str, html: str, serial: str
    ) -> None: ...

    @abstractmethod
    async def update_simple_index(self, html: str, serial: str) -> None: ...


class RedisBanderCache(BanderCache):
    def __init__(self, hostname: str = "localhost") -> None:
        self.hostname = hostname
        self._pool: redis.Redis | None = None

    async def __aenter__(self) -> "RedisBanderCache":
        self._pool = redis.from_url(
            f"redis://{self.hostname}", decode_responses=True
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._pool is not None:
            await self._pool.aclose()

    @property
    def pool(self) -> redis.Redis:
        if self._pool is None:
            raise RuntimeError(
                "RedisBanderCache not initialised - use as a context manager"
            )
        return self._pool

    async def get_package_simple_index(self, package_name: str) -> str:
        package_html_key, package_serial_key = self.canon_key_names(package_name)
        serial = cast("str | None", await self.pool.get(package_serial_key))
        if serial is None:
            raise CacheMiss("No serial - need to generate HTML")

        global_serial = cast("str | None", await self.pool.get(self.serial_key))
        if global_serial is None or int(global_serial) > int(serial):
            raise CacheMiss("Index is out of date")

        html = cast("str | None", await self.pool.get(package_html_key))
        if not html:
            raise CacheMiss("HTML is invalid - Regenerate")

        return html

    async def get_simple_index(self) -> str:
        html = cast("str | None", await self.pool.get(self.index_key))
        if not html:
            raise CacheMiss("Global Index HTML is invalid - Regenerate")

        return html

    async def update_package_simple_index(
        self, package_name: str, html: str, serial: str
    ) -> None:
        package_html_key, package_serial_key = self.canon_key_names(package_name)
        LOG.info(f"Updating Simple Index html for {package_html_key} serial {serial}")
        await asyncio.gather(
            self.pool.set(package_html_key, html),
            self.pool.set(package_serial_key, serial),
        )

    async def update_simple_index(self, html: str, serial: str) -> None:
        LOG.info(f"Updating Root Simple Index html for serial {serial}")
        await asyncio.gather(
            self.pool.set(self.index_key, html),
            self.pool.set(self.index_serial_key, serial),
        )


async def test_redis() -> None:
    ci_test_html = "<html><head><title>Testing</title></head></html>"
    ci_test_serial = "69"

    async with RedisBanderCache() as rbc:
        before_serial: str | None = None
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
