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

Planeteria depends on some libraries.  On Debian, you can get them all with this:

     aptitude install python-feedparser python-utidylib python-simplejson \
     python-beautifulsoup python-lxml python-htmltmpl python-dateutil

On a Mac, the following can be installed with pip using the following command: 

    pip install feedparser pytidylib simplejson beautifulsoup lxml python-dateutil

Note that tidy must also be installed for pytidylib to work.  Visit http://countergram.com/open-source/pytidylib/docs/index.html for additional info.

We found that htmltmpl needs to be downloaded and manually installed on a Mac. Go to http://sourceforge.net/projects/htmltmpl/files/htmltmpl/ and download the 1.22 version in the list (dated 2001-12-17).  WARNING: *Do not* click the link at the top of the page that says "Looking for the latest version?"; although the version number says 1.22 so it looks like what you need, the link will actually download the php version of htmltmpl, not the python version, which is what this project uses.  The download should have the file name htmltmpl-1.22.tar.gz; you should not see php anywhere in the filename.
    Once it's downloaded, uncompress it, then navigate to the folder and run the setup.py file with the command:
    python setup.py install

### Loading the site on your machine
Note that without running it on a virtual server, form submission won't work, however you can view the site just fine.

Run Planeteria/planeteria.py which should generate the html files for the site.  Then open Planeteria/www/index.html in your browser.  

### Running the site on an Apache server

The site requires sqlite3.  What version of Apache??

Settings:

in your /etc/hosts file, 

in your httpd.conf file, make sure it points to the /extra/httpd-vhosts.conf file like so:
# Virtual hosts
Include /private/etc/apache2/extra/httpd-vhosts.conf
(this is the file path for Mac OS X; make sure this is the correct file path for your setup)

in your /extra/httpd-vhosts.conf file, add the following settings:

<VirtualHost *:80>
    ServerName 
    ServerAlias
    ServerAdmin james@jamesvasile.com
    DocumentRoot /path/to/Planeteria/www 
#    ErrorLog ${APACHE_LOG_DIR}/planeteria.org-error.log
#    TransferLog ${APACHE_LOG_DIR}/planeteria.org-access.log
    LogLevel debug
</VirtualHost>

<Directory /path/to/Planeteria/www>    
    Options +ExecCGI +FollowSymLinks
    AllowOverride All
    AddHandler cgi-script cgi py pl
</Directory>

Once your settings are saved, reboot the server and follow the directions above to load the site.

### Set base href

You can tell Planeteria what domain and directory it lives in by
creating a `data/base_href` file and placing the domain there.  On James'
system, for example, that file contains `http://planeteria.org`.

This is probably an optional step.  Planeteria defaults to the root
directory, which should be fine for a lot of people.

### Permissions

Make sure your web server can read/execute everything and that it can write to `/data`.

### Automatic updates

Add a line to your crontab:

     15 * * * * cd /path/to/Planeteria; ./planeteria.py
