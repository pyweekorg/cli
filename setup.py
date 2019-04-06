from setuptools import setup

import pyweek


setup(
    name='pyweek',
    description="CLI for Pyweek.",
    version=pyweek.__version__,
    author='Daniel Pope',
    author_email='mauve@mauveweb.co.uk',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://pyweek.org/",
    project_urls={
        "Bug Tracker": "https://github.com/pyweekorg/cli/issues",
        "Documentation": "https://pyweek.readthedocs.io/en/latest/cli.html",
        "Source Code": "https://github.com/pyweekorg/cli",
    },
    py_modules=['pyweek'],
    python_requires='>=3.6',
    install_requires=[
        'click',
        'requests',
        'progressbar2',
        'packaging',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'pyweek = pyweek:cli',
        ]
    }
)
