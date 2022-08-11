#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-11
# !/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-07-23
import re
from setuptools import find_packages, setup

with open("fourcats_utils/__init__.py", "r") as file:
    regex_version = r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]'
    version = re.search(regex_version, file.read(), re.MULTILINE).group(1)

with open("README.md", "rb") as file:
    readme = file.read().decode("utf-8")

setup(
    name="fourcats-utils",
    version=version,
    packages=find_packages(),
    description="A common Python toolkit package based on personal habits.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="ShiWeiDong",
    author_email="shiweidong1993@gmail.com",
    url="https://github.com/FourCats-Py/FourCats-Utils",
    download_url="https://github.com/FourCats-Py/FourCats-Utils/archive/{}.tar.gz".format(version),
    keywords=["fourcats", "utils"],
    install_requires=["loguru>=0.6.0", "mergedict>=1.0.0", "PyYAML>=6.0", "urllib3>=1.26.11"],
    python_requires=">=3.8"
)
