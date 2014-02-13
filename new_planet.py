#!/usr/bin/python
"""
Planeteria new planet interface
Copyright 2009 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

"""

__authors__ = [ "James Vasile <james@hackervisions.org>"]
__license__ = "AGPLv3"


import os,sys,re, shutil
from util import our_db
import cgi
import cgitb
cgitb.enable()

#from config import *
import config as cfg
from config import opt
log = cfg.logging.getLogger('planeteria')
from util import Msg
err=Msg(web=True)

import templates

class BadSubdirNameError(Exception):
   pass

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
      valid = False

   return valid

def make_planet(subdir, output_dir=None,
                name="", user="", email=""):
   """
   Makes a planet on disk and in the db, copying the skeleton
   directory on disk.  Does not seed the planet with default values
   for owner or email.
   """
   if not validate_input(subdir):
      raise BadSubdirNameError, subdir

   if not output_dir:
      output_dir = opt['output_dir']

   path = os.path.join(output_dir, subdir)
   
   with our_db('planets') as db:
      if os.path.exists(path) and not subdir in db:
         log.debug("Exists on disk but not in db, attempting to delete")
         shutil.rmtree(path)

   try:
      shutil.copytree(opt['new_planet_dir'], path, symlinks=True)
   except(OSError), errstr:
      if os.path.exists(path):
         msg = "%s planet already exists. Please choose another subdirectory name." % subdir
         err.add(msg)
         log.info(msg)
         return False
      err.add("Couldn't create planet: %s" % errstr)
      return False

   from planet import Planet
   if not name: name = 'Planet %s' % subdir
   p = Planet({'direc':subdir,
               'name':name,
               'user':user,
               'email':email,
               'password':'passme',
               'feeds':{'http://hackervisions.org/?feed=rss2':{'image':'http://www.softwarefreedom.org/img/staff/vasile.jpg','name':'James Vasile', 'feedurl':'http://hackervisions.org/?feed=rss2'}}
               })
    
   p.save()
   mopt = dict(opt.items()+p.__dict__.items())

   templates.Welcome(mopt).write(path, 'index.html')

   log.info("Made planet: %s" % path)
   return True

    
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
   print templates.Index(doc).render().encode('utf-8', 'ignore')

if __name__ == "__main__":
   main()
