#!/usr/bin/env python3
# Copyright (c) 2014-present, Facebook, Inc.

from setuptools import setup


setup(
    name="banderfront",
    version="0.0.1.dev0",
    description="Simple HTTP frontend for a Python Bandersnatch Mirror",
    packages=["banderfront"],
    package_dir={"": "src"},
    url="http://github.com/cooperlees/banderfront/",
    author="Cooper Lees",
    author_email="me@cooperlees.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp",
        "bandersnatch",
        "gunicorn",
        "uvloop",
    ],
    extras_require={
        "s3": ["aioboto3"],
        "swift": ["python-swiftclient"],
    }
)
