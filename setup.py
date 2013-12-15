#!/usr/bin/python

from setuptools import setup

setup(
    name='wiflight_client',
    version='0.1dev',
    description='Library for accessing the Wi-Flight REST API',
    author='Kim Vandry',
    author_email='vandry@TZoNE.ORG',
    packages=['wiflight',],
    license='Creative Commons Attribution-ShareAlike license',
    test_suite='tests',
)
