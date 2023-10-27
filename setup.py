import re

from setuptools import find_packages, setup

requirements = []
with open("requirements.txt") as file:
    requirements = file.read().splitlines()

setup(
    name="tallulah-classifier",
    version="0.1.0",
    install_requires=requirements,
    packages=find_packages(),
    package_data={},
    python_requires=">=3.11",
    author="Jaap Oosterbroek",
    author_email="jaap@secureailabs.com",
    description="",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://nowhere.not",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: SAIL :: Propritary",
        "Operating System :: OS Independent",
    ],
)
