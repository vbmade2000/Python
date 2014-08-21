from setuptools import setup

setup(
    name = 'microdata',
    version = '0.4.0',
    description = "html5lib extension for parsing microdata",
    author = "Ed Summers",
    author_email = "ehs@pobox.com",
    url = "http://github.com/edsu/microdata",
    py_modules = ['microdata'],
    scripts = ['microdata.py'],
    test_suite = 'test',
    install_requires = ['html5lib'],
)
