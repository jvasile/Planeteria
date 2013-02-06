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

#### Package installation on Debian
To install them on Debian, you can get them all by typing (or pasting) the following into a terminal window:

    aptitude install python-feedparser python-utidylib python-simplejson \
    python-beautifulsoup python-lxml python-htmltmpl python-dateutil

#### Package installation on Mac OS X
To install them on Mac OS X, most can be installed with pip, but one needs to be downloaded first. Go to [http://sourceforge.net/projects/htmltmpl/files/htmltmpl/](http://sourceforge.net/projects/htmltmpl/files/htmltmpl/) and download the 1.22 version  (dated 2001-12-17).  
> WARNING: *Do not* click the link at the top of the page that says "Looking for the latest version?"; although the version number says 1.22 which is the correct version number, the link will actually download htmltmpl 1.22 for PHP, not the Python version which is what this project uses. The download should have the file name *htmltmpl-1.22.tar.gz*; you should not see *php* in the filename.
Once you have downloaded the htmltmpl tarball, note the file path for the pip install. Copy and paste the following command into a terminal window, and before you hit Enter, replace *path/to/htmltmpl-1.22.tar.gz* with the file path on your system.

    pip install feedparser pytidylib simplejson beautifulsoup lxml python-dateutil path/to/htmltmpl-1.22.tar.gz


The last step for Mac users is to install tidy, which is required for [pytidylib](http://countergram.com/open-source/pytidylib/docs/index.html) to work.  We used [Homebrew](http://mxcl.github.com/homebrew/) to install tidy but it requires an extra step because it's not in the default Homebrew repository.  First, enter 
    brew tap homebrew/dupes  
which tells homebrew to look in the dupes library, then:
    brew install homebrew/dupes/tidy  
which installs tidy.


### Loading the site on your machine
Note that without running it on a virtual server, form submission won't work, so you won't be able to create or administer a planet, however you can view the homepage just fine.

Run *planeteria.py* which should generate the html files for the site and place them in the */www* folder.  Then open */www/index.html* in a browser window.


### Running the site on an Apache server

The site requires sqlite3.


### Permissions

Make sure that the Planeteria directory is accessible by the web server (read/execute permission).  You also need to give the server write permission for the following directories: 
    /data
    /www
    /log


#### Settings

If you are setting up a virtual host, in your /etc/hosts file, add a new line underneath *127.0.0.1 localhost* that says 
    127.0.0.1 planeteria.local

> For those setting up a virtual host on a Mac for the first time, [this site](http://www.456bereastreet.com/archive/201104/apache_with_virtual_hosts_php_and_ssi_on_mac_os_x_106/) walks you through the process in more detail. 

In your httpd.conf file, make sure it points to the /extra/httpd-vhosts.conf file like so:
    # Virtual hosts
    Include /private/etc/apache2/extra/httpd-vhosts.conf
(this is the file path for Mac OS X; make sure this is the correct file path to the httpd-vhosts.conf)

In your */extra/httpd-vhosts.conf* file, add the following settings:

    <VirtualHost *:80>
        ServerName  planeteria.local (it should match the server name in your /etc/hosts file)
        ServerAdmin youremail@example.com
        DocumentRoot "/path/to/Planeteria/www"
        ErrorLog ${APACHE_LOG_DIR}/planeteria-error.log
        TransferLog ${APACHE_LOG_DIR}/planeteria-access.log
        LogLevel debug
    </VirtualHost>

    <Directory "/path/to/Planeteria/www/">    
        Options +ExecCGI +FollowSymLinks
        AllowOverride All
        Order allow,deny
        Allow from all
        AddHandler cgi-script cgi py pl
    </Directory>

Make sure to replace */path/to/Planeteria* with the file path to the location of the cloned Planeteria repo. Be especially attentive to the trailing slashes and quotation marks around the file paths, they may vary from machine to machine and can make the difference of whether the virtual host can find the root directory or not.  

Once your settings are saved, reboot the server and follow the directions above to load the site.

### Set base href

You need to tell Planeteria what domain and directory it lives in by creating a `data/base_href` file with the domain.  It must start with *http://*.  On the server which runs the site, that file contains *http://planeteria.org*.  On Aleta's virtual server, the file contains *http://planeteria.local* which just adds http:// to the server name used in her */etc/hosts* file.  

### Automatic updates

In a sandbox environment, you can choose to generate the html files as needed by running *planeteria.py* in the Terminal.  However if you want to deploy the site on a server to run on its own, you will need to set up a cron job to run planeteria.py automatically every so often.  Planeteria.org runs it every 15 minutes.

To set this up, add a line to your crontab:

    15 * * * * cd /path/to/Planeteria; ./planeteria.py

Happy hacking!
