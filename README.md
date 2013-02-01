# Planeteria Readme

## Installation

### Grab the code

     git clone git://github.com/jvasile/Planeteria.git

### Permissions

Make sure your web server can read/execute everything and that it can write to `/data`.

### Automatic updates

Add a line to your crontab:

     15 * * * * cd /path/to/planeteria; ./planeteria.py

### Dependencies

Planeteria depends on some libraries.  On my Debian box, I can get them all with this:

     aptitude install python-feedparser python-utidylib python-simplejson \
     python-beautifulsoup python-lxml python-htmltmpl python-dateutil



### Set base href

You can tell Planeteria what domain and directory it lives in by
creating a `data/base_href` file and placing the domain there.  On my
system, for example, that file contains `http://planeteria.org`.

This is probably an optional step.  Planeteria defaults to the root
directory, which should be fine for a lot of people.

