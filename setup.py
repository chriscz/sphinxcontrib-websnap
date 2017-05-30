# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = """
This contrib extension, sphinxcontrib.websnap provides Sphinx
directives for scraping, archiving and linking to archived sites.

It's currently in **alpha**.

You can find the documentation from the following URL:

http://github.com/chriscz/sphinxcontrib-websnap
"""

requires = [
    'Sphinx >= 1.6',
    'lxml',
    'bs4'
]

setup(
    name='sphinxcontrib-websnap',
    version='0.1.0',
    url='http://github.com/chriscz/sphinxcontrib-websnap',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-websnap',
    license='MPL',
    author='Chris Coetzee',
    author_email='chriscz93@gmail.com',
    description='Sphinx directives for archiving and linking to websites',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
