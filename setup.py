# pylint: disable=missing-module-docstring

from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="helmYAMLizer",
    packages=find_packages(),
    install_requires=requirements,
)
