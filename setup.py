from setuptools import setup


setup(
    name='pyweek',
    short_description="CLI for Pyweek.",
    author='Daniel Pope',
    author_email='mauve@mauveweb.co.uk',
    py_modules=['pyweek'],
    python_requires='>=3.6',
    install_requires=[
        'click',
        'requests',
        'progressbar2',
    ],
    entry_points={
        'console_scripts': [
            'pyweek = pyweek:cli',
        ]
    }
)
