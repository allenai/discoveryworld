#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

setup(
    name='discoveryworld',
    version=open(os.path.join("discoveryworld", "version.py")).readlines()[0].split("=")[-1].strip("' \n"),
    packages=find_packages(),
    include_package_data=True,
    description="DiscoveryWorld - Making new discovery.",
    install_requires=open('requirements.txt').readlines(),
)
