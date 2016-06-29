from setuptools import setup

setup(name='autoprotocol_utilities',
      version='2.1.7',
      description='Helper methods to construct protocols using autoprotocol-python.',
      url='https://github.com/transcriptic/autoprotocol-utilities',
      author='Conny Scheitz, Vanessa Biggers and all past and present Application Scientists',
      author_email='conny@transcriptic.com, vanessa@transcriptic.com',
      license='MIT',
      packages=['autoprotocol_utilities'],
      tests_require=['pytest'],
      install_requires=['autoprotocol>=3.7'],
      zip_safe=False)
