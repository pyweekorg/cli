from setuptools import setup
import re


def find_version():
    """Extract the version number from the CLI source file."""
    with open('pyweek.py') as f:
        for l in f:
            mo = re.match('__version__ = *(.*)?\s*', l)
            if mo:
                return eval(mo.group(1))
        else:
            raise Exception("No version information found.")


setup(
    name='pyweek',
    description="CLI for Pyweek.",
    version=find_version(),
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
