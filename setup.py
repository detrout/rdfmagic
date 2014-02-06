from setuptools import setup

setup(
  name='rdfmagic',
  version='0.1',
  description='IPython magic functions to make it easier to query Redland librdf triple stores',
  author='Diane Trout',
  author_email='diane@ghic.org',
  packages=['rdfmagic'],
  install_requires=['IPython >= 0.12'],
  test_suite='test.test_rdfmagic.suite'
)
