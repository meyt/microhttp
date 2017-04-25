from setuptools import setup, find_packages
readme = open('README.rst').read()

setup(
    name='microhttp',
    version='0.1.2',
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
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'nanohttp',
        'dogpile.cache',
        'sqlalchemy',
        'webtest',
        'mako'
    ]
)
