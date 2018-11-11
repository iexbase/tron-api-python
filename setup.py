#!/usr/bin/env python
# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

"""
    setup
    =====

    Tron: A Python API for interacting with Tron (TRX)

    :copyright: © 2018 by the iEXBase.
    :license: MIT License
"""

import os
import platform
from setuptools import (
    find_packages,
    setup,
)

py_version = platform.python_version()

PACKAGE_VERSION = '2.0.5'

tests_require = [
    'coverage',
    'pep8',
    'pyflakes',
    'pylint',
    'pytest',
    'pytest-cov',
]

install_requires = [
    "toolz>=0.9.0,<1.0.0;implementation_name=='pypy'",
    "cytoolz>=0.9.0,<1.0.0;implementation_name=='cpython'",
    "hexbytes>=0.1.0,<1.0.0",
    "requests",
    "pycryptodome",
    "base58",
    "eth-account>=0.2.1,<0.4.0",
    "eth-utils>=1.2.0,<2.0.0",
    "ecdsa",
    "pysha3",
    'attrdict',
]

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.rst')

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()


setup(
    name='tronapi',
    version=PACKAGE_VERSION,
    description='A Python API for interacting with Tron (TRX)',
    long_description=PACKAGE_LONG_DESCRIPTION,
    keywords='tron tron-api tron-api-python iexbase',
    url='https://github.com/iexbase/tron-api-python',
    author='Shamsudin Serderov',
    author_email='steein.shamsudin@gmail.com',
    license='MIT License',
    zip_safe=False,
    python_requires='>=3.5.3,<4',
    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['examples']),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    },
)
