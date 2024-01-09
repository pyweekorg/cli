"""A command line interface to PyWeek.

Download and verify entries for a given challenge:
"""
import sys
import os
import re
from pathlib import Path
import time
from packaging import version
import zipfile

import requests
import click
import progressbar

__version__ = '0.5.3'
PYWEEK_URL = 'https://pyweek.org'
CLI_PYPI_URL = 'https://pypi.org/pypi/pyweek/json'

PROGRESSBAR_WIDGETS = [
    progressbar.Percentage(),
    ' ', progressbar.Bar(marker='\u2588'),
    ' ', progressbar.ETA(),
    ' ', progressbar.DataSize(),
    ' ', progressbar.FileTransferSpeed(),
]

sess = requests.Session()


def version_check():
    """Check that this CLI is up-to-date."""
    if os.environ.get('PYWEEK_SKIP_VERSION_CHECK') is not None:
        return
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

    directory.mkdir(parents=True, exist_ok=True)

    resp = sess.get(f'{PYWEEK_URL}/{challenge}/downloads.json')
    resp.raise_for_status()
    downloads = resp.json()

    errors = 0
    for name, files in downloads.items():
        entry_dir = directory / sanitise_name(name)
        entry_dir.mkdir(exist_ok=True)

        for f in files:
            name = f['name']
            url = f['url']
            size = f['size']
            target = entry_dir / name
            try:
                st = target.stat()
            except FileNotFoundError:
                pass
            else:
                if st.st_size == size:
                    # Already downloaded, skip
                    continue

            res = download_file(url, target, size)
            if not res:
                errors += 1

    if errors:
        click.echo(
            click.style(
                f"{errors} errors occurred while downloading files.",
                fg='red'
            )
        )
    else:
        click.echo(
            click.style(
                "All files downloaded successfully.",
                fg='green'
            )
        )


@cli.command()
@click.argument(
    'file',
    type=Path,
)
def verify(file: Path):
    """
    Determines if a given zip file is in the proper format.
    """

    errors = 0

    if not file.exists():
        error(f"File {file} does not exist.")
        sys.exit()

    if not file.suffix == '.zip':
        error(f"File is not a zip file.", errors)
        errors += 1

    # Check that the file name follows the proper naming convention
    pattern = re.compile(r'^[A-Za-z0-9-]+-[0-9]+\.[0-9]+(\.[0-9]+)?\.zip$')
    match = pattern.match(file.name)
    if not match:
        error(f"""File does not follow the proper naming convention.
    The file name should be in the format: {{Name-of-Entry}}-{{major.minor}}.zip
    Example: "My-Game-1.0.zip" or "my-game-1.0.1.zip\"""", errors)
        errors += 1

    # Open the zip file
    try:
        zipped_file = zipfile.ZipFile(file)
    except zipfile.BadZipFile:
        error(f"File is not a valid zip file.", errors)
        sys.exit(1)
    except IsADirectoryError:
        error(f"File is a directory.", errors)
        sys.exit(1)

    # Check that the zip file contains a single top-level directory
    # This directory should be named the same as the zip file
    top_level_dirs = []
    for name in zipped_file.namelist():
        name = name.split('/')[0]
        if name not in top_level_dirs:
            top_level_dirs.append(name)

    if len(top_level_dirs) != 1:
        error(f"File contains multiple top-level directories.", errors)
        errors += 1
    else:
        # Check that the top-level directory is named the same as the zip file
        if top_level_dirs[0] != file.stem:
            error(f"""File contains a top-level directory named "{top_level_dirs[0]}".
    This directory should be named "{file.stem}/".""", errors)
            errors += 1

        # Check that the top-level dir contains the needed files (run_game.py, requirements.txt, README.(md|txt))
        files_in_top_level_dir = []
        for name in zipped_file.namelist():
            n = name.split('/')[1]
            if n not in files_in_top_level_dir and name.count('/') == 1 and n:
                files_in_top_level_dir.append(n)

        if 'run_game.py' not in files_in_top_level_dir:
            error(f"""File does not contain a "run_game.py" file.""", errors)
            errors += 1

        if 'requirements.txt' not in files_in_top_level_dir:
            error(f"""File does not contain a "requirements.txt" file.""", errors)
            errors += 1

        if 'README.md' not in files_in_top_level_dir and 'README.txt' not in files_in_top_level_dir:
            error(f"""File does not contain a "README.md" or "README.txt" file.""", errors)
            errors += 1

    if errors:
        click.echo()
        click.echo(
            click.style(
                f"{errors} error{"s" if errors > 1 else ""} occurred while verifying file {file}.",
                fg='red'
            )
        )

    else:
        click.echo(
            click.style(
                f"File {file} is valid.",
                fg='green'
            )
        )


def error(msg, errors=0):
    """Print an error message and exit."""

    if errors:
        click.echo()
    click.echo(
        click.style(
            msg,
            fg='red'
        )
    )


CHUNK_SIZE = 10240


def download_file(url, target, size):
    """Download the given file.

    Throttle to about the given rate in KB/s.

    """
    headers = {}
    if target.exists():
        start = target.stat().st_size
        if start < size:
            headers['Range'] = f'bytes={start}-{size}'
        else:
            start = 0
    else:
        start = 0

    resp = sess.get(url, stream=True, headers=headers)
    if resp.status_code not in (200, 206):
        click.echo(
            click.style(
                f"Warning: error downloading {url}",
                fg='red'
            )
        )
        return False

    length = int(resp.headers['Content-Length'])
    assert length == size - start, \
        f"Invalid length {length}, expected {size - start}"

    name = f'{target.parent.name}{os.sep}{target.name}'

    if resp.status_code == 206:
        click.echo(
            "Resuming " + click.style(name, fg='cyan')
        )
        mode = 'ab'
    else:
        click.echo(
            "Downloading " + click.style(name, fg='cyan')
        )
        mode = 'wb'

    widgets = PROGRESSBAR_WIDGETS
    with progressbar.ProgressBar(widgets=widgets, max_value=size) as bar, \
        target.open(mode) as out:
        while True:
            # We read chunks of 100KiB at a time. We cannot use
            # resp.iter_content() because this is not raw enough; it will
            # decode Content-Encoding: gzip for us, which means we would be
            # writing .tar data for a .tar.gz download from S3.
            chunk = resp.raw.read(102400)
            if not chunk:
                break
            assert isinstance(chunk, bytes)
            out.write(chunk)
            bar.update(out.tell())
        assert out.tell() == size, \
            f"Incorrect size written, expected {size}, wrote {out.tell()}"
    return True


if __name__ == '__main__':
    cli()
