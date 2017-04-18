from setuptools import setup
readme = open('README.rst').read()

setup(name='microhttp',
      version='0.1.1',
      description='A tool-chain for nanohttp',
      long_description=readme,
      url='http://github.com/meyt/microhttp',
      author='Mahdi Ghane.g',
      license='MIT',
      keywords='nanohttp microhttp web tool-chain',
      classifiers=[
          'Development Status :: 1 - Planning',
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
          'mako'
      ],
      packages=['microhttp'],
      )



