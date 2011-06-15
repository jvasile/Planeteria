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
               % (url,
                  url,
                  feed['name'],
                  '',
                  feed['image'],
                  '',
                  ''
                  ))
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

    #doc['timestamp'] = os.path.getmtime(config_fname)

    doc['Feeds']=[]
    count = 0
    for feed in planet.feeds:
        f={} 
        f['idx']=count
        f['row_class'] = "face%d" % (count % 2)
        f['faceurl'] = feed.image[planet.direc]
        f['feedurl'] = feed.url
        #f['facewidth'] = f['faceheight'] = ''
        f['section'] = feed.url
        f['name'] = feed.name
        doc['Feeds'].append(f)
        count += 1;
    return doc

    

############################
 ##
##  Config.ini Stuff
 ##
############################
def update_config(config):
    """Grab new values from the form and stick them in config.
    Modifies config in place.  Does not save to file."""
    for k,v in {'PlanetName':'name', 'OwnerName':'owner_name', 'OwnerEmail':'owner_email',
                'Pass':'password', 'Sidebar':'sidebar'}.items():
        config.parser.set('Planet', v.strip(), Form.getvalue(k,''))

    if Form.getvalue('ChangePass','') != '':
        config.parser.set('Planet', 'password', Form.getvalue('ChangePass',''))

    feed_count = 0;
    form_field = ['feedurl', 'name', 'faceurl'] #, 'facewidth', 'faceheight']

    while (Form.has_key('section%d' % feed_count)):
        if Form.getvalue('delete%d' % feed_count) == '1':
            #err('delete%d' % feed_count)
            section = Form.getvalue('section%d' % feed_count)
            if config.parser.has_section(section):
                config.parser.remove_section(section)
        else:
            f = config.feed_options(Form.getvalue('feedurl%d' % feed_count))
            section = Form.getvalue('section%d' % feed_count)

            # If it's a new section, use the feedurl as the name of the section
            if section == 'section%d' % feed_count:
                section = Form.getvalue('feedurl%d' % feed_count)
                config.parser.add_section(section)

            # Copy the values from the form into config
            for field in form_field:
                if not config.parser.has_section(section):
                    config.parser.add_section(section)
                config.parser.set(section, field, 
                                  Form.getvalue('%s%d' % (field, feed_count),'').strip())
        feed_count += 1;
    return config

def write_ini(config):
    "Writes config.ini for this planet"
    try:
        shutil.copy(config_fname, config_fname+".bak")
    except (IOError, os.error), why:
        err("Could not backup config file %s: %s" % (config_fname, str(why)))

    for sub in config.subscriptions():
        if config.feed_options(sub)['feedurl'] != sub:
            config.parser.add_section(config.feed_options(sub)['feedurl'])
            for k,v in config.feed_options(sub, False).items():
                config.parser.set(config.feed_options(sub)['feedurl'], k, v.strip())
            config.parser.remove_section(sub)
    remove_feed_url(config)

    try:
        f = open(config_fname, 'wb')
        config.parser.write(f)
    except (IOError, os.error), why:
        err("Could not write config file %s: %s" % (config_fname, str(why)))
    else:
        err("Updated configuration.  The planet page will reflect your changes shortly.")

def update_planet_page():
    # Do planet.py -n and update index.html, atom.xml and opml.xml
    os.chdir(planet_dir);
    err("!"+planet_dir)
    bin = "../planeteria.d/vendor/venus/planet.py"
    opt = "-n -v"
    os.system("%s %s" % (bin, opt))

    #pid = os.spawnlp(os.P_NOWAIT, "%s/planet.py" % bin_path, "planet.py", "-n -v")

def save(config):
    "Save changes to config.ini"
    write_ini(config)
    #update_planet_page()

def add_feed_url(config):
    """set feedurl to the url of the feed for each subscription"""
    for sub in config.subscriptions():
        config.parser.set(sub, 'feedurl', sub)

def remove_feed_url(config):
    """Remove any feedurls set in the subscriptions"""
    for sub in config.subscriptions():
        config.parser.remove_option(sub, 'feedurl')

############################
 ##
##  Setup and Prep
 ##
############################
import shutil, planet

## Setup and globals
VERSION = "0.2";
Form=''

def update_planet(planet):
    p = Planet(planet)
    p.update()
    p.generate()


def main():
    import cgi
    import cgitb
    cgitb.enable()

    global Form
    Form = cgi.FieldStorage()


    #print "Content-type: text/html\n\n" 
    #from planet import config
    #config.load(config_fname)

    ## Handle form input
    if Form.has_key('PlanetName'):
        orig_pass = config.planet_options()['password']
        config = update_config(config);

        if Form.getvalue('Timestamp') != str(os.path.getmtime(config_fname)):
            err("Admin page has expired!  Perhaps somebody else is " +
                "editing this planet at the same time as you?  Please " +
                "reload this page and try again.")
        elif Form.getvalue('Pass','') == '':
            err("Please enter your password at the bottom of the page.")
        elif Form.getvalue('Pass') != orig_pass:
            err("Invalid password")
        else:
            save(config)
            #add_feed_url(config)
    else:
         pass
         #add_feed_url(config)

    from planet import Planet
    planet = Planet(direc=opt['planet_subdir'])

    ## Template
    print interpolate(opt['template_fname'], template_vars(planet, Form))

if __name__ == "__main__":
    main()
