# CLAUDE.md

Guidance for working in this repo with Claude Code.

## What this is

**banderfront** is an async HTTP frontend (aiohttp + gunicorn) that serves a
Python [Bandersnatch](https://github.com/pypa/bandersnatch) mirror's simple index
directly from Redis, removing bandersnatch's need to write static HTML to a
filesystem. See `README.md` for the user-facing overview and the architecture
diagram.

## Project facts

- **Python 3.14 only** (`requires-python = ">=3.14"`). Drops 3.7/3.8.
- **Packaging:** `pyproject.toml` (PEP 517/518, setuptools backend). `setup.py`
  is legacy and being phased out — prefer editing `pyproject.toml`.
- **Typed package:** ships `src/banderfront/py.typed`; mypy runs in `strict`
  mode (see `[tool.mypy]` in `pyproject.toml`).
- **Source layout:** `src/banderfront/` — `cache.py` (Redis cache layer),
  `routes.py`, `server.py`.

## Redis: use `redis`, not `aioredis`

This project's async Redis client is **redis-py via `redis.asyncio`**, imported
as `import redis.asyncio as redis`.

- `aioredis` is **dead** — `aioredis` 2.0.1 was the final release and the project
  was archived and merged into redis-py 4.2+. `redis.asyncio` *is* the former
  aioredis.
- `aioredis==2.0.1` **does not import on Python 3.14**: it raises
  `TypeError: duplicate base class TimeoutError` because `asyncio.TimeoutError`
  is now an alias of the builtin `TimeoutError`. So it cannot be used here at all.
- redis-py ships a `py.typed` marker, so it type-checks cleanly under mypy strict
  (`aioredis` was untyped, which produced `no-untyped-call` errors).

### API notes (when editing `cache.py`)

- Connect: `redis.from_url(f"redis://{host}", decode_responses=True)`.
- Close: `await pool.aclose()` (not `.close()`, which is deprecated in redis-py 8).
- **Why the `cast(...)` calls:** `Redis.get()` is honestly typed as returning
  `bytes | str | None`. mypy can't know that the runtime `decode_responses=True`
  argument guarantees `str`, so we `cast("str | None", await pool.get(...))` to
  record that contract. `redis.Redis` is **not** generic in redis-py 8, so it
  can't be parametrised to `str` instead.

## Running CI locally

CI (`.github/workflows/ci.yml`) runs on Python 3.14 and has two checks: a mypy
strict step and an integration test. Reproduce both in a throwaway venv:

```sh
python3 -m venv /tmp/tb
/tmp/tb/bin/python -m pip install --upgrade pip setuptools wheel
/tmp/tb/bin/python -m pip install -r requirements.txt

# 1. mypy strict (the type-checking gate)
/tmp/tb/bin/python -m mypy src/banderfront

# 2. integration test
/tmp/tb/bin/python -m pip install .
/tmp/tb/bin/python ci.py
```

`requirements.txt` is exact-pinned and is the source of truth for the CI
environment; `pyproject.toml` carries the loose runtime dependencies. Keep the
two in sync when adding/removing a dependency.

> `ci.py` is currently a stub (`print("CI Coming soon 🤘🏻")`) — it does not yet
> exercise Redis, so the integration step does not need a running Redis server.

## Local Redis (for `cache.py:test_redis()` / real runs)

```sh
docker run --name redis -d -p 6379:6379 redis
/tmp/tb/bin/python -m banderfront.cache   # runs test_redis() against localhost
```
