#! /usr/bin/env python
#coding=utf-8

from setuptools import setup
import linciclient

scripts = []

setup_args = {
    'name': "linciclient",
    'version': linciclient.__version__,
    'description': "linci client tools",
    'long_description': "linci client tools for ",
    'author': linciclient.__author__,
    'author_email': linciclient.__author_email__,
    'url': linciclient.__url__,
    'license': linciclient.__license__,
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Console',
        'Framework :: Uliweb',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Testing',
    ],

    'packages': [
        "linciclient",
    ],
    'scripts': scripts,
}

setup(**setup_args)
