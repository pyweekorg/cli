"""A command line interface to PyWeek.

Currently just a command for downloading the entries.

"""
import sys
import re
from pathlib import Path
import time
from packaging import version

import requests
import click
import progressbar


__version__ = '0.2.0'
PYWEEK_URL = 'https://pyweek.org'
CLI_PYPI_URL = 'https://pypi.org/pypi/pyweek/json'


PROGRESSBAR_WIDGETS = [
    progressbar.Percentage(),
    ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),
    ' ', progressbar.ETA(),
    ' ', progressbar.FileTransferSpeed(),
]


sess = requests.Session()


def version_check():
    """Check that this CLI is up-to-date."""
    resp = sess.get(CLI_PYPI_URL)
    resp.raise_for_status()
    pkginfo = resp.json()
    v = version.parse(pkginfo['info']['version'])
    this_version = version.parse(__version__)
    if v > this_version:
        click.echo(
            click.style(
                f"There is a newer version {v} of this tool on PyPI. "
                "Please update before continuing:\n\n"
                "    pip install --upgrade pyweek",
                fg='red'
            )
        )
        sys.exit(1)


@click.group()
def cli():
    """Command line interface to PyWeek."""
    version_check()


def sanitise_name(name):
    """Strip name of characters that might be invalid in paths.

    >>> sanitise_name('What the Frog!?')
    'what-the-frog'

    """
    return re.sub(r'[^\w]+', '-', name.lower()).strip('-')


@cli.command()
@click.option(
    '-d', '--directory',
    type=Path,
    help="The directory to download into. " +
         "If omitted, download into a directory named after the challenge."
)
@click.argument(
    'challenge',
#    help="The challenge number to download entries for."
)
def download(challenge, directory):
    """Download all Pyweek entries for a competition."""
    if not directory:
        directory = Path.cwd() / str(challenge)

    if directory.exists():
        raise click.ClickException(
            f"Target directory {directory} exists!"
        )

    directory.mkdir(parents=True)

    resp = sess.get(f'{PYWEEK_URL}/{challenge}/downloads.json')
    resp.raise_for_status()
    downloads = resp.json()

    for name, files in downloads.items():
        entry_dir = directory / sanitise_name(name)
        entry_dir.mkdir()

        for f in files:
            name = f['name']
            url = f['url']
            target = entry_dir / name
            download_file(url, target)
    click.echo(
        click.style(
            "All files downloaded successfully.",
            fg='green'
        )
    )


def download_file(url, target):
    """Download the given file."""

    resp = sess.get(url, stream=True)
    if resp.status_code != 200:
        print(f"Warning: error downloading {url}")
        return False

    length = int(resp.headers['Content-Length'])

    widgets = [target.name, ' ', *PROGRESSBAR_WIDGETS]
    with progressbar.ProgressBar(widgets=widgets, max_value=length) as bar, \
            target.open('wb') as out:
        for chunk in resp.iter_content(10240):
            out.write(chunk)
            bar.update(out.tell())
            time.sleep(0.2)  # throttle to about 50KB/s
    print(f"Downloaded {target}")
    return True


if __name__ == '__main__':
    cli()
