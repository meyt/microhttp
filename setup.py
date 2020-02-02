from setuptools import setup, find_packages

dependencies = [
    "nanohttp == 1.11.1",
    "pymlconf == 1.2.*",
    "sqlalchemy",
    "mako",
]


def read_version(module_name):
    from re import match, S
    from os.path import join, dirname

    with open(join(dirname(__file__), module_name, "__init__.py")) as f:
        return match(r".*__version__.*('|\")(.*?)('|\")", f.read(), S).group(2)


setup(
    name="microhttp",
    version=read_version("microhttp"),
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
