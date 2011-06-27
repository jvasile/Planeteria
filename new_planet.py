#!/usr/bin/python
"""
Planeteria admin interface
Copyright 2009 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

"""

__authors__ = [ "James Vasile <james@hackervisions.org>"]
__license__ = "AGPLv3"


import os,sys,re
import cgi, shutil
import cgitb
cgitb.enable()

from config import *
log = logging.getLogger('planeteria')
from util import Msg
err=Msg(web=True)

import templates

def template_vars(subdir="", form_vals={}):
   "Returns a dict with the template vars in it"
   doc=dict(form_vals.items() + opt.items())
   if not 'turing' in doc:
      doc['turing']=''
   doc['subdirectory'] = subdir
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

   path = os.path.join(opt['output_dir'], subdir)

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

   templates.Welcome(mopt).write(path, 'index.html')
   return True

    
## Setup and globals
VERSION = "0.1";

def main():
   global Form
   Form = cgi.FieldStorage()

   subdir = Form.getvalue("subdirectory", '').lower()

   log.debug("Form keys and vals: %s" % (dict([(k,Form.getvalue(k,'')) for k in Form.keys()])))
   if 'submit' in Form.keys():
      if Form.getvalue("turing",'').lower() != "yes":
         err.add("I can't believe you failed the Turing test.  Maybe you're a sociopath?")
         log.debug("Turing test failed for %s" % subdir)
      elif validate_input(subdir):
         if make_planet(subdir):
            print "Location: http://%s/%s/admin.py\n\n" % (opt['domain'], subdir)
            return
   
   sys.stdout.write("Content-type: text/html\n\n")
   doc = template_vars(subdir, dict([(k,Form.getvalue(k,'')) for k in Form.keys()]))
   log.debug("doc: %s" % doc)
   print templates.Index(doc).render().encode('latin-1', 'ignore')

if __name__ == "__main__":
   main()
