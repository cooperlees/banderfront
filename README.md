# banderfront
Frontend Webserver for Bandersnatch Mirrors

Replaces the need for bandersnatch to generate static simple HTML and Apache or NGINX to do rewrites.

- Removes the need current dependency bandersnatch has for a filesystem to store static HTML on

- As of today we don't do HTTPS but happy to take a PR to enable that.
  - I would envision this to run behind a faster HTTPS proxy for HTTPS

banderfront defaults to using [gunicorn](https://gunicorn.org/), but could be used with other
async WSGI implementations.

## Docker

Docker build works and defaults to two workers with gunicorn.

## Development

Install all into a virtualenv and start like any other gunicorn aiohttp web application.

- uvloop is default but optional ...

```sh
python3 -m venv /tmp/tbf/
/tmp/tbf/bin/pip install --upgrade pip setuptools
/tmp/tbf/bin/pip install -e .  # Extras if needed more than filesystem support
/tmp/tbf/bin/gunicorn --bind=[::]:8000 --access-logfile=- --name=banderfront \
    --workers=2 --worker-class=aiohttp.worker.GunicornUVLoopWebWorker "banderfront.server:serve"
```

### Expected start logs

```
cooper-mbp1:banderfront cooper$ /tmp/tbf/bin/gunicorn --bind=[::]:8000 --access-logfile=- --name=banderfront \
>     --workers=2 --worker-class=aiohttp.worker.GunicornUVLoopWebWorker "banderfront.server:serve"
[2020-05-31 14:07:42 -0700] [5457] [INFO] Starting gunicorn 20.0.4
[2020-05-31 14:07:42 -0700] [5457] [INFO] Listening at: http://[::]:8000 (5457)
[2020-05-31 14:07:42 -0700] [5457] [INFO] Using worker: aiohttp.worker.GunicornUVLoopWebWorker
[2020-05-31 14:07:42 -0700] [5461] [INFO] Booting worker with pid: 5461
[2020-05-31 14:07:42 -0700] [5462] [INFO] Booting worker with pid: 5462
[2020-05-31 14:07:42,156] INFO: Finished setting up logging for the software portal (server.py:42)
[2020-05-31 14:07:42,171] INFO: Finished setting up logging for the software portal (server.py:42)
[2020-05-31 14:07:57 -0700] [5457] [INFO] Handling signal: winch
::1 [31/May/2020:21:08:09 +0000] "GET / HTTP/1.1" 200 933 "-" "curl/7.64.1"
::1 [31/May/2020:21:14:24 +0000] "GET /69 HTTP/1.1" 200 254 "-" "curl/7.64.1"
```

### Example Responses

```text
cooper-mbp1:~ cooper$ curl localhost:8000

 ____                     _                                 _          _        ____          ____   ___    __  __  _
| __ )   __ _  _ __    __| |  ___  _ __  ___  _ __    __ _ | |_   ___ | |__    |  _ \  _   _ |  _ \ |_ _|  |  \/  |(_) _ __  _ __   ___   _ __
|  _ \  / _` || '_ \  / _` | / _ \| '__|/ __|| '_ \  / _` || __| / __|| '_ \   | |_) || | | || |_) | | |   | |\/| || || '__|| '__| / _ \ | '__|
| |_) || (_| || | | || (_| ||  __/| |   \__ \| | | || (_| || |_ | (__ | | | |  |  __/ | |_| ||  __/  | |   | |  | || || |   | |   | (_) || |
|____/  \__,_||_| |_| \__,_| \___||_|   |___/|_| |_| \__,_| \__| \___||_| |_|  |_|     \__, ||_|    |___|  |_|  |_||_||_|   |_|    \___/ |_|
                                                                                       |___/
cooper-mbp1:~ cooper$ curl localhost:8000/69
.------..------.
|6.--. ||9.--. |
| (\/) || :/\: |
| :\/: || (__) |
| '--'6|| '--'9|
`------'`------'
```
