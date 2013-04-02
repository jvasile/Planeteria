# Planeteria Readme


## About Planeteria

A _planet_ is a collection of posts from many different blogs, all
somewhat related to one topic. It's a great way to keep tabs on a
subject, a community, a technology, a team, a project or anything else
that attracts a diverse range of bloggers.

Planeteria.org is a hosted planet reader. Planeteria allows anyone to
make a planet, host it and administer it on Planeteria.org. After you
make your planet, tell people about it. That's the whole point of
community-building!

Planeteria was created by James Vasile (james at hackervisions dot
net) in 2010 and has been maintained in his copious spare time since
its creation.

## Command Line Options to planeteria.py

Planeteria is run as a command line tool (planeteria.py) and two CGI
scripts (admin.py and new_planet.py).  The command line tool is used
as follows:

Usage: planeteria.py [options]

Options:

 * -h, --help        show this help message and exit
 * --force           force downloading of cached upstream feeds
 * --no-update       prevent downloading of upstream feeds
 * --delete-missing  delete planets from db if they are not in file system
 * --clean           remove missing planets, unused feeds

The `--clean` flag doesn't remove old posts from the cache (just
unused feeds), and it doesn't delete unused planets, but in a future
version, it will.

## About Planeteria's code

This is a free open source project licensed under the
[AGPLv3 license](http://www.fsf.org/licensing/licenses/agpl-3.0.html).

This software was originally built on
[Venus](http://intertwingly.net/code/venus/). Venus is great if you're
only running one planet, I highly recommend it.  However trying to
scale up the code for a single planet to make one system do many
planets proved to be tricky, so those dependencies were discarded for
more flexibility. The code is less robust as a result and could use
some love.

In 2013, Aleta Dunne (aleta dot dunne at gmail dot com) took on fixing
up the site as an internship project for the
[GNOME Outreach Program for Women (OPW)](http://live.gnome.org/OutreachProgramForWomen).
We always welcome more help, though!

Please let us know about bugs on the
[Github issue tracker](https://github.com/jvasile/Planeteria/issues),
or submit a patch!

We have a roadmap in ROADMAP.md, please feel ping us if you want to
tackle any of those!

### Unit Tests

There are some tests in the `test` directory.  Run them from the main
directory with `nosetests .` and you will see the start of some unit
testing.  Please don't use the tests on a live, deployed install.
They create and destroy test planets.

The tests include tests of the web functionality and expect the site
to live on planeteria.localhost.  To run those tests, you'll want to
do be logged in as the same user that your apache instance runs under
(try `sudo su www-data; bash`).  Otherwise, there is a permissions
mismatch when the user running the tests tries to delete a file
created by the web server and the 644 permissions prevent it.  If you
get permission denied errors when running nosetests, this might be the
problem.

If you want to see the debug output while running nosetest, do `tail
-f log/planeteria.log` in another screen or console.

## Installation

Planeteria is compatible with Python versions 2.3 - 2.7.  For an
overview of its components, see `doc/overview.dia`.


### Grab the code from the master repo:

    git clone git://github.com/jvasile/Planeteria.git


### Dependencies

Planeteria depends on several libraries.  Follow the instructions for
your OS below.  We've only tested the installation on Debian and Mac
OS X so far; we welcome any contributors who would like to help
develop installation instructions for other operating systems.

We recommend installing these in a virtual environment (virtualenv) to
avoid conflicts with dependencies for other projects run on the same
machine. To learn more about installing and using ```virtualenv```, go
to
[http://www.virtualenv.org/en/latest/](http://www.virtualenv.org/en/latest/)

#### Package installation on Debian To install them on Debian, you can
get them all by typing (or pasting) the following into a terminal
window:

    aptitude install python-feedparser python-utidylib python-simplejson \
    python-beautifulsoup python-lxml python-htmltmpl python-dateutil
    
If you want to run the tests, you'll need to set base href (see below)
and install `python-nose` and `python-twill` too:

    aptitude install python-nose python-twill

#### Package installation on Mac OS X

Most packages can be installed on a Mac with ```pip```, however one of
them needs to be downloaded before running pip. Go to
[http://sourceforge.net/projects/htmltmpl/files/htmltmpl/](http://sourceforge.net/projects/htmltmpl/files/htmltmpl/)
and download the 1.22 version (dated 2001-12-17).

WARNING: *Do not* click the link at the top of the page that says
"Looking for the latest version?"  Although the version number seems
to be the correct version number, the link will actually download
htmltmpl 1.22 for PHP, not the Python version which is what this
project uses. The download should have the file name
```htmltmpl-1.22.tar.gz```; you should not see ```php``` in the
filename.

Once you have downloaded the htmltmpl tarball, note the file path for
the pip install. Copy and paste the following command into a terminal
window, and before you hit Enter, replace
```path/to/htmltmpl-1.22.tar.gz``` with the file path on your system.

    pip install feedparser pytidylib simplejson beautifulsoup lxml python-dateutil path/to/htmltmpl-1.22.tar.gz


The last step for Mac users is to install ```tidy```, which is
required for
[pytidylib](http://countergram.com/open-source/pytidylib/docs/index.html)
to work.  We used [Homebrew](http://mxcl.github.com/homebrew/) to
install tidy but it requires an extra step because it's not in the
default Homebrew repository.  First, enter

    brew tap homebrew/dupes  

which tells homebrew to look in the dupes library, then:

    brew install homebrew/dupes/tidy  

which installs tidy.


### Loading the site on your machine

Note that without running it on an Apache server, form submission
won't work, so you won't be able to create or administer a planet,
however you can view the static pages just fine.

Run ```planeteria.py``` which should generate the html files for the
site and place them in the ```/www``` folder.  Then open
```/www/index.html``` in a browser window.


### Running the site on an Apache server virtual host

The site requires sqlite3.


#### Permissions

Make sure that the Planeteria directory is accessible by the web
server (read/execute permission).  You also need to give the server
write permission for the following directories:

    /data
    /www
    /log


#### Server Configuration

*For those setting up a virtual host on a Mac,
 [this site](http://www.456bereastreet.com/archive/201104/apache_with_virtual_hosts_php_and_ssi_on_mac_os_x_106/)
 walks you through the process in more detail than described below.*

In your /etc/hosts file, add a new line underneath ```127.0.0.1
localhost``` that says

    127.0.0.1 planeteria.local

In your httpd.conf file, make sure it points to the
/extra/httpd-vhosts.conf file like below.  Verify the file path!

    # Virtual hosts
    Include /private/etc/apache2/extra/httpd-vhosts.conf

(The second line is commented out by default.)

In your /extra/httpd-vhosts.conf file, add the following settings:

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

Make sure to replace /path/to/Planeteria with the full file path to
the location of the cloned Planeteria repo. Be especially attentive to
the trailing slashes and quotation marks around the file paths, they
may vary from machine to machine and can make the difference of
whether the server can find the root directory or not.

Once your settings are saved, reboot the server and follow the
directions above to load the site.

### Set base href

You need to tell Planeteria what domain and directory it lives in by
creating a ```data/base_href``` file with the domain.  It must start
with ```http://```.  On the server which runs the site, that file
contains ```http://planeteria.org```.  On Aleta's virtual host, the
base_href file contains ```http://planeteria.local``` which just adds
http:// to the server name used in her ```/etc/hosts``` file.

### Automatic updates

In a sandbox environment, you can choose to generate the html files as
needed by running ```planeteria.py``` in the Terminal.  However if you
want to deploy the site on a server to run on its own, you will need
to set up a cron job to run planeteria.py automatically every so
often.  Planeteria.org runs it every 15 minutes.

To set this up, add a line like this to your crontab:

    15 * * * * cd /path/to/Planeteria; ./planeteria.py --clean

Happy hacking!
