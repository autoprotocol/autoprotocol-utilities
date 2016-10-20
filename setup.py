from setuptools import setup

setup(name='autoprotocol_utilities',
      version='2.3.1',
      description='Helper methods to construct protocols using autoprotocol-python.',  # NOQA
      url='https://github.com/transcriptic/autoprotocol-utilities',
      author='All past and present Application Scientists',
      author_email='vanessa@transcriptic.com',
      license='MIT',
      packages=['autoprotocol_utilities'],
      tests_require=['pytest'],
      install_requires=['autoprotocol>=3.7'],
      zip_safe=False)
