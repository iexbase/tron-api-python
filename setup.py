#!/usr/bin/env python
import platform

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    import setuptools

py_version = platform.python_version()

_TRON_VERSION = '1.0.5'

REQUIRED = [
    'urllib3'
]

with open('README.md') as fileobj:
    README = fileobj.read()

setuptools.setup(
    name='tronapi',
    version=_TRON_VERSION,
    include_package_data=True,
    packages=setuptools.find_packages(),
    description='A Python API for interacting with Tron (TRX)',
    long_description=README,
    url='https://github.com/iexbase/tron-api-python',
    author='Shamsudin Serderov',
    author_email='steein.shamsudin@gmail.com',
    install_requires=REQUIRED,
    license='MIT',
    keywords='tron tron-api tron-api-python iexbase'
)
