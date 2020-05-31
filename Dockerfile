FROM python:3

RUN mkdir -p /src/src
COPY setup.py /src
COPY requirements.txt /src
COPY src/ /src/src

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /src/requirements.txt
RUN pip install --no-cache-dir /src/

RUN rm -rf /src

CMD ["gunicorn", \
     "--bind=[::]:8000", \
     "--access-logfile=-", \
     "--name=banderfront", \
     "--workers=2", \
     "--worker-class=aiohttp.worker.GunicornUVLoopWebWorker", \
     "banderfront.server:serve"]
