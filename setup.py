#!/usr/bin/env python

from setuptools import setup

setup(name='liquidcrystal_i2c',
      version='0.2',
      description='Library for the LCD-Display "LCM1602 IIC V2"',
      author='Patrick Buech',
      url='https://github.com/pl31/python-liquidcrystal_i2c',
      packages=['liquidcrystal_i2c'],
      license='MIT License',
      requires='pysmbus',
      zip_safe=True)
