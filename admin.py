#!/usr/bin/python
"""
Planeteria admin interface
Copyright 2011 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>
Version 0.2

"""

__authors__ = [ "James Vasile <james@hackervisions.org>"]
__license__ = "AGPLv3"


import os, sys
sys.path.insert(0,"..")

#os.chdir('..')

from config import *

if __name__ == "__main__":
   try:
      planet_dir = os.sep.join(os.environ['SCRIPT_FILENAME'].split(os.sep)[:-1])
   except KeyError:
      try:
         planet_dir = os.sep.join((os.getcwd() + os.environ['SCRIPT_NAME']).split(os.sep)[:-1])
      except:
         planet_dir = os.getcwd()
   global debug
   debug = True
   opt['planet_subdir'] = planet_dir.split(os.sep)[-1]
   opt['template_fname'] = os.path.join(opt['template_dir'], 'admin.tmpl')
   output_dir = planet_dir

#######################
##
## Utility Functions
##
########################
from util import merge_dict, dict_val, write_file, interpolate

error=''
def err(msg):
   """Add msg to the error string, which can be displayed via template.
   TODO: log the error w/ planet's logger"""
   global error
   error = error + "<p>%s</p>\n" % msg

#########################
 ##
## TEMPLATE FUNCTIONS
 ##
##########################
def render_text_input (id, label, default="", size = 25):
   "Return html for a text input field"
   return ('<label for="%s">%s:</label>' % (id, label)
          + '<input type="text" size="%d" name="%s" id="%s" value="%s">' % (size, id, id, default)
          + "\n")
def render_pass_input (id, label, default="", size = 25):
   "Return html for a password input field"
   return ('<label for="%s">%s:</label>' % (id, label)
           + '<input type="password" size="%d" name="%s" id="%s" value="%s">' % (size, id, id, default)
           + "\n")

def render_push_feed(planet):
   "Return javascript for pushing feeds into array"
   ret = ''

   for url, feed in planet.feeds.items():
      ret = (ret + "      new_feed('%s', '%s', '%s', '%s', '%s', '%s', '%s');\n" 
             % (url, url, feed['name'], '', feed['image'], '', ''))
   return ret
         
def template_vars(planet, config):
    "Returns a dict with the template vars in it"
    doc = opt.copy()
    global error
    doc['admin']=1
    doc['error'] = error
    doc['name'] = planet.name
    merge_dict(doc, planet.__dict__)
    merge_dict(doc, config)
    if doc['password'] == 'passme':
        doc['passme'] = 1
    doc['planet_name_input'] = render_text_input("PlanetName", "Planet name", doc['name'], 40)
    doc['owner_name_input'] = render_text_input("OwnerName", "Your name", doc['user'], 40)
    doc['owner_email_input']=render_text_input("OwnerEmail", "Your email", doc['email'], 40)
    doc['change_pass_input'] = render_text_input("ChangePass", "New Password", Form.getvalue('ChangePass',''))
    doc['pass_input'] = render_pass_input("Pass", "Password", Form.getvalue('Pass', ''))
    doc['push_feeds'] = render_push_feed(planet)

    doc['timestamp'] = planet.last_config_change
    doc['Feeds']=[]
    count = 0
    for url, feed in planet.feeds.items():
        f={} 
        f['idx']=count
        f['row_class'] = "face%d" % (count % 2)
        f['faceurl'] = feed['image']
        f['feedurl'] = url
        #f['facewidth'] = f['faceheight'] = ''
        f['section'] = url
        f['name'] = feed['name']
        doc['Feeds'].append(f)
        count += 1;
    return doc

def import_opml(file, planet):
   from xml.etree import ElementTree

   with open('opml.xml', 'rt') as f:
      tree = ElementTree.parse(f)

   for node in tree.getiterator('outline'):
      name = node.attrib.get('text')
      url = node.attrib.get('xmlUrl')
      if url:
         if not url in planet.feeds:
            planet.feeds[url]={'url':url, 'name':name, 'image':''}
         else:
            planet.feeds[url]['url'] = url
            if name: planet.feeds[url]['name'] = name
   planet.save()

############################
 ##
##  Config.ini Stuff
 ##
############################
def update_config(planet):
    """Grab new values from the form and stick them in config.
    Modifies config in place.  Does not save to file."""
    for k,v in {'PlanetName':'name', 'OwnerName':'user', 'OwnerEmail':'email',
                'Pass':'password', 'Sidebar':'sidebar'}.items():
        planet.__dict__[v] = Form.getvalue(k,'')

    if Form.getvalue('ChangePass','') != '':
        planet.password = Form.getvalue('ChangePass','')

    feed_count = 0;
    form_field = ['feedurl', 'name', 'faceurl'] #, 'facewidth', 'faceheight']

    while (Form.has_key('section%d' % feed_count)):
        url = Form.getvalue('feedurl%d' % feed_count)
        if Form.getvalue('delete%d' % feed_count) == '1':
            del planet.feeds[url]
        else:
            if not url in planet.feeds:
                planet.feeds[url]={'url':url, 'name':Form.getvalue('name%d' % feed_count), 'image':Form.getvalue('faceurl%d' % feed_count)}

            # Copy the values from the form into config
            for field in form_field:
                planet.feeds[url][field] = Form.getvalue('%s%d' % (field, feed_count),'').strip()
        feed_count += 1;
    return planet

############################
 ##
##  Setup and Prep
 ##
############################
import shutil, planet

## Setup and globals
VERSION = "0.2";
Form=''


def main():
    import cgi
    import cgitb
    cgitb.enable()

    global Form
    Form = cgi.FieldStorage()

    from planet import Planet
    planet = Planet(direc=opt['planet_subdir'])

    #print "Content-type: text/html\n\n" 
    #from planet import config
    #config.load(config_fname)

    ## Handle form input
    if Form.has_key('PlanetName'):
        orig_pass = planet.password
        planet = update_config(planet)

        if Form.getvalue('Timestamp') != str(planet.last_config_change):
            err("Admin page has expired!  Perhaps somebody else is " +
                "editing this planet at the same time as you?  Please " +
                "reload this page and try again.")
            if debug: err("%s != %s" % (Form.getvalue('Timestamp'), planet.last_config_change))
        elif Form.getvalue('Pass','') == '':
            err("Please enter your password at the bottom of the page.")
        elif Form.getvalue('Pass') != orig_pass:
            err("Invalid password")
        else:
            planet.save(update_config_timestamp=True)

    ## Template
    print interpolate(opt['template_fname'], template_vars(planet, Form))

if __name__ == "__main__":
    main()
