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

Planeteria depends on some libraries.  Follow the instructions for your OS below.  We've only tested the installation on Debian and Mac OS X so far; we welcome any contributors who would like to help develop installation instructions for other operating systems. 

We recommend installing these in a virtual environment (virtualenv) to avoid conflicts with dependencies for other projects run on the same machine. To learn more about installing and using _virtualenv_, go to [http://www.virtualenv.org/en/latest/](http://www.virtualenv.org/en/latest/)

#### Package installation on Debian
To install them on Debian, you can get them all by typing (or pasting) the following into a terminal window:

    aptitude install python-feedparser python-utidylib python-simplejson \
    python-beautifulsoup python-lxml python-htmltmpl python-dateutil

#### Package installation on Mac OS X
Most packages can be installed on a Mac with _pip_, however one of them needs to be downloaded before running pip. Go to [http://sourceforge.net/projects/htmltmpl/files/htmltmpl/](http://sourceforge.net/projects/htmltmpl/files/htmltmpl/) and download the 1.22 version  (dated 2001-12-17).  
_WARNING: *Do not*_ click the link at the top of the page that says "Looking for the latest version?"  Although the version number seems to be the correct version number, the link will actually download htmltmpl 1.22 for PHP, not the Python version which is what this project uses. The download should have the file name _htmltmpl-1.22.tar.gz_; you should not see _php_ in the filename.
Once you have downloaded the htmltmpl tarball, note the file path for the pip install. Copy and paste the following command into a terminal window, and before you hit Enter, replace _path/to/htmltmpl-1.22.tar.gz_ with the file path on your system.

    pip install feedparser pytidylib simplejson beautifulsoup lxml python-dateutil path/to/htmltmpl-1.22.tar.gz


The last step for Mac users is to install _tidy_, which is required for [pytidylib](http://countergram.com/open-source/pytidylib/docs/index.html) to work.  We used [Homebrew](http://mxcl.github.com/homebrew/) to install tidy but it requires an extra step because it's not in the default Homebrew repository.  First, enter 

    brew tap homebrew/dupes  

which tells homebrew to look in the dupes library, then:

    brew install homebrew/dupes/tidy  

which installs tidy.


### Loading the site on your machine
Note that without running it on a virtual server, form submission won't work, so you won't be able to create or administer a planet, however you can view the homepage just fine.

Run _planeteria.py_ which should generate the html files for the site and place them in the _/www_ folder.  Then open _/www/index.html_ in a browser window.


### Running the site on an Apache server

The site requires sqlite3.


### Permissions

Make sure that the Planeteria directory is accessible by the web server (read/execute permission).  You also need to give the server write permission for the following directories: 

    /data
    /www
    /log


#### Server Configuration

*For those setting up a virtual host on a Mac, [this site](http://www.456bereastreet.com/archive/201104/apache_with_virtual_hosts_php_and_ssi_on_mac_os_x_106/) walks you through the process in more detail than described below.* 

If you are setting up a virtual host, in your /etc/hosts file, add a new line underneath _127.0.0.1 localhost_ that says 

    127.0.0.1 planeteria.local

In your httpd.conf file, make sure it points to the /extra/httpd-vhosts.conf file like so:

    # Virtual hosts
    Include /private/etc/apache2/extra/httpd-vhosts.conf

(The second line is usually commented out.)

In your _/extra/httpd-vhosts.conf_ file, add the following settings:

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

Make sure to replace _/path/to/Planeteria_ with the full file path to the location of the cloned Planeteria repo. Be especially attentive to the trailing slashes and quotation marks around the file paths, they may vary from machine to machine and can make the difference of whether the server can find the root directory or not.  

Once your settings are saved, reboot the server and follow the directions above to load the site.

### Set base href

You need to tell Planeteria what domain and directory it lives in by creating a `data/base_href` file with the domain.  It must start with _http://_.  On the server which runs the site, that file contains _http://planeteria.org_.  On Aleta's virtual server, the file contains _http://planeteria.local_ which just adds http:// to the server name used in her _/etc/hosts_ file.  

### Automatic updates

In a sandbox environment, you can choose to generate the html files as needed by running _planeteria.py_ in the Terminal.  However if you want to deploy the site on a server to run on its own, you will need to set up a cron job to run planeteria.py automatically every so often.  Planeteria.org runs it every 15 minutes.

To set this up, add a line to your crontab:

    15 * * * * cd /path/to/Planeteria; ./planeteria.py

Happy hacking!
