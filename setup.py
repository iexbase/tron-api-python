#!/usr/bin/env python
import os
import platform

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    import setuptools


py_version = platform.python_version()

PACKAGE_VERSION = '2.0.2'
PACKAGE_REQUIRED = [
    'urllib3',
    'pycryptodome',
    'base58'
]

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.md')

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()


setuptools.setup(
    name='tronapi',
    version=PACKAGE_VERSION,
    description='A Python API for interacting with Tron (TRX)',
    long_description=PACKAGE_LONG_DESCRIPTION,
    url='https://github.com/iexbase/tron-api-python',

    keywords='tron tron-api tron-api-python iexbase',

    author='Shamsudin Serderov',
    author_email='steein.shamsudin@gmail.com',
    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=PACKAGE_REQUIRED,
)
