#! /usr/bin/env python
#coding=utf-8

from setuptools import setup
import linciclient

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
    'entry_points' : {
        'console_scripts': [
            'linci_client_config = linciclient.config:main',
            'linci_arti_open = linciclient.artifact.open:main',
            'linci_arti_upload = linciclient.artifact.upload:main',
            'linci_arti_set_ready = linciclient.artifact.set_ready:main',
            'linci_arti_fix = linciclient.artifact.fix:main',
            'linci_arti_download = linciclient.artifact.download:main',
            'linci_arti_close = linciclient.artifact.close:main',
            'linci_worker = linciclient.worker:main',
        ],
    },
}

setup(**setup_args)
