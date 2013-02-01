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

Planeteria depends on some libraries.  

To install them on Debian, you can get them all by typing (or pasting) the following into a terminal window:

     aptitude install python-feedparser python-utidylib python-simplejson \
     python-beautifulsoup python-lxml python-htmltmpl python-dateutil

To install them on Mac OS X, most can be installed with pip, but one needs to be downloaded first. Go to http://sourceforge.net/projects/htmltmpl/files/htmltmpl/ and download the 1.22 version in the list (dated 2001-12-17).  WARNING: *Do not* click the link at the top of the page that says "Looking for the latest version?"; although the version number says 1.22 so it looks like what you need, the link will actually download the php version of htmltmpl, not the python version, which is what this project uses.  The download should have the file name htmltmpl-1.22.tar.gz; you should not see php anywhere in the filename. 

    pip install feedparser pytidylib simplejson beautifulsoup lxml python-dateutil path/to/htmltmpl-1.22.tar.gz

Note that tidy must also be installed for pytidylib (http://countergram.com/open-source/pytidylib/docs/index.html) to work.  We used Homebrew (get it here: http://mxcl.github.com/homebrew/) to install tidy but it requires an extra step because it's not in the default repository.  The steps are: 
 	brew tap homebrew/dupes  
which tells homebrew to look in the dupes library, then:
	brew install homebrew/dupes/tidy  
which installs tidy.

### Loading the site on your machine
Note that without running it on a virtual server, form submission won't work, however you can view the site just fine.

Run Planeteria/planeteria.py which should generate the html files for the site.  Then open Planeteria/www/index.html in your browser.  

### Running the site on an Apache server

The site requires sqlite3.

Settings:

in your /etc/hosts file, ____

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
    ErrorLog ${APACHE_LOG_DIR}/planeteria-error.log
    TransferLog ${APACHE_LOG_DIR}/planeteria-access.log
    LogLevel debug
</VirtualHost>

<Directory /path/to/Planeteria/www>    
    Options +ExecCGI +FollowSymLinks
    AllowOverride All
    AddHandler cgi-script cgi py pl
</Directory>

Once your settings are saved, reboot the server and follow the directions above to load the site.

### Set base href

You need to tell Planeteria what domain and directory it lives in by creating a `data/base_href` file and placing the domain there.  On James'
system, for example, that file contains `http://planeteria.org`.  On Aleta's system, the file contains http://planeteria.local which matches what's in the etc/hosts file.

### Permissions

Make sure that the Planeteria directory is publicly accessible by the web server (read/execute permission).  You also need to give the server write permission for the following directories: 
/data
/www
/log

### Automatic updates

In a sandbox environment, you can choose to generate the html files as needed by running planeteria.py.  However if you want to deploy the site on a server to run on its own, you will need to set it up to run planeteria.py automatically every so often.  Right now Planeteria.org runs it every 15 minutes.  

Add a line to your crontab:

     15 * * * * cd /path/to/Planeteria; ./planeteria.py
