# PyWeek CLI


Command line interface for pyweek.org.

So far, the only feature is downloading entries:

    pyweek download 29


This downloads into a new directory `29` inside the current directory.


## History

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
