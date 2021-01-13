from setuptools import setup, find_packages

setup(name='Nodal_NEAT',
      packages=find_packages(),
      install_requires=['graphviz', 'matplotlib'],
      version='1.0.0'
      )
# TODO: wheel in graphviz backend
