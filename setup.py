from setuptools import setup, find_packages

setup(name='astrocom',
      version='1.0.0',
      url='https://github.com/rfetick/astrocom.git',
      license='See LICENSE file',
      author='Romain JL Fetick (France)',
      description='Python package to command telescope mounts',
      packages=find_packages(exclude=['example','test']),
      requires=['numpy','astropy'],
      zip_safe=False)

