#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="riot_pal",
    version="0.0.1",
    author="RIOT OS",
    author_email="devel@riot-os.org",
    description="A protocol abstraction layer for RIOT and low level devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RIOT-OS",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers"
    ],
)
