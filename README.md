# PyWeek CLI


Command line interface for pyweek.org.

So far, the only feature is downloading entries:

    pyweek download 29


This downloads into a new directory `29` inside the current directory.


## History

* 0.5.3 - Revert certificate verification
* 0.5.2 - Disable certificate verification (temporary)
* 0.5.1 - Fix: downloading .tar.gz files from S3 decompresses them and
  then crashes
* 0.5.0 - remove rate limits, as the server's download bandwidth is no longer
  constrained
* 0.4.0 - resume partial downloads
* 0.3.0 - resume a download run
* 0.2.0 - check for upgrades
* 0.1.0 - initial downloader CLI


## Installing

PyWeek CLI can be installed with pip:

    pip install pyweek

## Development

Install [uv](https://docs.astral.sh/uv/), then run:

    uv sync --frozen
    uv run --frozen python -m unittest -v
    uv build

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Use
`uv lock` after changing dependencies. The version comes from Git tags; the
`pyweek/_version.py` file is generated at build time and is not committed.

## Releasing

The release workflow uses PyPI Trusted Publishing. Before the first release,
add a trusted publisher to the existing `pyweek` project on PyPI with:

- GitHub owner: `pyweekorg`
- Repository: `cli`
- Workflow: `publish.yml`
- Environment: `pypi`

In the GitHub Releases UI, create and publish a release from `master` with a
new tag such as `v0.5.4`. The workflow builds the wheel and source distribution
from that tag and uploads them to PyPI. Drafts and pre-releases are not
published. The version in the tag must use three numeric components; no version
number needs to be edited in source code.
