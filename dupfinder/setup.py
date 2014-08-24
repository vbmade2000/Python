"""
dupfinder
"""

from setuptools import setup, find_packages

INSTALL_REQUIRES = []
TESTS_REQUIRES = []

version = "0.1.0"

setup(
    name='dupfinder',
    version=version,
    description='Duplicate file finder',
    author='Malhar Vora',
    author_email='mlvora.2010@gmail.com',
    url='',
    download_url=(
        ''
    ),
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRES,
    extras_require={},
    license='GNU',
    keywords=['duplicate', 'file', 'finder'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
		"Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
		"Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
    ]
)