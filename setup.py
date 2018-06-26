import re
from os.path import join, dirname
from setuptools import setup, find_packages
readme = open('README.rst').read()

# reading package version (without reloading it)
with open(join(dirname(__file__), 'microhttp', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


dependencies = [
    'nanohttp >= 0.29.0',
    'dogpile.cache',
    'sqlalchemy',
    'mako'
]

setup(
    name='microhttp',
    version=package_version,
    description='A tool-chain for creating web application based on nanohttp',
    long_description=readme,
    url='http://github.com/meyt/microhttp',
    author='Mahdi Ghane.g',
    license='MIT',
    keywords='nanohttp microhttp web tool-chain',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=dependencies
)
