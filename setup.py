from setuptools import setup

setup(name='grove_radar',
      version='0.0',
      packages=[
          'BGT24LTR11'],
      install_requires=[
          'pyserial>=3.0'
      ],
      zip_safe=False)
