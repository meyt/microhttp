import re

from os.path import join, dirname
from setuptools import setup, find_packages

package_name = "microhttp"
dependencies = [
    "nanohttp ~= 1.10.1",
    "pymlconf == 1.2.*",
    "sqlalchemy",
    "mako",
]


# reading package version (without reloading it)
with open(join(dirname(__file__), package_name, "__init__.py")) as v_file:
    package_version = (
        re.compile(r".*__version__ = '(.*?)'", re.S)
        .match(v_file.read())
        .group(1)
    )


setup(
    name=package_name,
    version=package_version,
    description="A tool-chain for creating web application based on nanohttp",
    long_description=open("README.rst").read(),
    url="http://github.com/meyt/microhttp",
    author="Mahdi Ghane.g",
    license="MIT",
    keywords="nanohttp microhttp web tool-chain",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=dependencies,
)
