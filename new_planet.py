#!/usr/bin/python
"""
Planeteria admin interface
Copyright 2009 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

"""

__authors__ = [ "James Vasile <james@hackervisions.org>"]
__license__ = "AGPLv3"


import os,sys,re

#import util
from util import interpolate
from util import write_file
from config import *
from util import Msg
err=Msg()
template_fname = os.path.join(opt['template_dir'], 'new.tmpl')

def template_vars(subdir="", email=""):
    "Returns a dict with the template vars in it"
    doc=opt.copy()
    
    doc['subdirectory'] = subdir
    doc['owner_email'] = email
    doc['error'] = err.html()
    return doc

def validate_input(subdir):

    if subdir == "":
        return False

    valid = True

    if re.search('\\W', subdir):
        err.add("Subdirectory can only contain letters, numbers and underscores.")
        valie = False

    return valid

def make_planet(subdir):

    path = os.path.join(opt['OUTPUT_DIR'], subdir)

    try:
        shutil.copytree(opt['new_planet_dir'], path, symlinks=True)
    except(OSError), errstr:
        if os.path.exists(path):
            err.add("%s already exists. Please choose another subdirectory name." % subdir)
            return False
        err.add("Couldn't create planet: %s" % errstr)
        return False

    from planet import Planet
    p = Planet({'direc':subdir,
                'name':'Planet %s' % subdir,
                'user':'',
                'email':'',
                'password':'passme',
                'feeds':{'http://hackervisions.org/?feed=rss2':{'image':'http://www.softwarefreedom.org/img/staff/vasile.jpg','name':'James Vasile', 'url':'http://hackervisions.org/?feed=rss2'}}
                })
    
    p.save()
    mopt = dict(opt.items()+p.__dict__.items())

    from util import make_static
    make_static(path, "index.html", "welcome.tmpl", mopt)
    return True

import cgi, shutil
    
## Setup and globals
VERSION = "0.1";

def main():
    global Form
    Form = cgi.FieldStorage()

    subdir = Form.getvalue("subdirectory", '').lower()
    #email = Form.getvalue("owner_email", '')

    if Form.getvalue("turing",'').lower() != "yes":
        err.add("I can't believe you failed the Turing test.  Maybe you're a sociopath?")
    elif validate_input(subdir):
        if make_planet(subdir):
            print "Location: http://%s/%s/admin.py\n\n" % (opt['domain'], subdir)
            return
    print "Content-type: text/html\n\n" 
    print interpolate(template_fname, template_vars(subdir))


def static():
    "Return a static version of this page suitable for caching"
    global Form
    Form = cgi.FieldStorage()
    return interpolate(template_fname, template_vars())

if __name__ == "__main__":
    main()
