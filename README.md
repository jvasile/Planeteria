# Planeteria Readme

## About Planeteria

Planets are ...
Planeteria.org is a hosted planet reader. 
[copy text from site about where the code comes from]
Created by James Vasile (james@hackervisions.net) in 2010 [check the date]

## Installation

Planeteria is compatible with Python versions 2.3 - 2.7.

### Grab the code from the master repo:

     git clone git://github.com/jvasile/Planeteria.git

### Dependencies

Planeteria depends on some libraries.  On my Debian box, I can get them all with this:

     aptitude install python-feedparser python-utidylib python-simplejson \
     python-beautifulsoup python-lxml python-htmltmpl python-dateutil

On a Mac, the following can be installed on your system with pip using the following command: 

    sudo pip install feedparser simplejson beautifulsoup lxml

We found that the remaining dependencies need to be downloaded and manually installed on a Mac:

    utidylib - go to http://sourceforge.net/projects/utidylib/?source=dlp and download the most current version. Unzip it, then navigate to the folder and run the setup.py file with the command
    $ sudo python setup.py install

    htmltmpl - go to http://sourceforge.net/projects/htmltmpl/files/htmltmpl/ and download the 1.22 version in the list (dated 2001-12-17). 
    WARNING: *Do not* click the link at the top of the page that says "Looking for the latest version?"; while the version numbers are the same, the link will download the php version, not the python version of htmltmpl, which is what this project uses.  The download should have the file name htmltmpl-1.22.tar.gz, you should not see php in the filename.
    Once it's downloaded, unzip it, then navigate to the folder and run the setup.py file with the command
   $ sudo python setup.py install

    dateutil - go to http://labix.org/python-dateutil and download version 1.5. Unzip it, then run the setup.py file in the folder to install with the command
    $ sudo python setup.py install

### Loading the site on your machine

Run planeteria.py which should generate the html files for the site.  Then open www/index.html in your browser.  

### Running the site on an Apache server

Settings:


### Set base href

You can tell Planeteria what domain and directory it lives in by
creating a `data/base_href` file and placing the domain there.  On my
system, for example, that file contains `http://planeteria.org`.

This is probably an optional step.  Planeteria defaults to the root
directory, which should be fine for a lot of people.

### Permissions

Make sure your web server can read/execute everything and that it can write to `/data`.

### Automatic updates

Add a line to your crontab:

     15 * * * * cd /path/to/planeteria; ./planeteria.py
