#!/usr/bin/env python

import os, sys, dbm, time, feedparser, htmltmpl, shutil, re, cgi, cgitb

from optparse import OptionParser
import simplejson as json
from urllib import urlopen

import config
from config import *

if not os.path.exists(DATA_DIR):
   os.mkdir(DATA_DIR)

generated=[]
planets = []
###############################################################################
def parse_options():
   parser = OptionParser()
   parser.add_option("", "--force", action="store_true", dest="force_update", help="force update of feeds", default=False),
   parser.add_option("", "--generate", action="store_true", dest="generate", help="generate static files", default=False),
   (options, args) = parser.parse_args()

   opt['force_check'] = options.force_update

   if len(args) >= 1:
      global planets
      planets.extend(args)

   if options.generate:
       for p in ['copyright', 'contact', 'thanks', 'tos']:
           make_page(p)
       make_static(config.OUTPUT_DIR, "index.html", "new.tmpl", config.opt)

       galaxy = Galaxy(planets)
       galaxy.load()
       #galaxy.dump()
       galaxy.update()
       galaxy.save()
       galaxy.generate()



###############################################################################
def html2xml(ins):
   """replace all the html entities with xml equivs"""
   ins = ins.replace("&nbsp;", "&#160;")
   return ins


def parse_updated_time(entry):
   try:
      return time.mktime(time.strptime(entry['updated'], "%a, %d %b %Y %H:%M:%S +0000"))
   except ValueError:
      return 0

def just_body(xhtml):
   return str(xhtml).split(' <body>')[1].split(' </body>')[0]

class berkeley_db:
   def __init__(self, fname):
      self.fname = fname
   def __enter__(self):
      self.db = dbm.open(os.path.join(DATA_DIR, self.fname), 'c')
      return self.db
   def __exit__(self, type, value, traceback):
      self.db.close()


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
   """From django, mildly modified. TODO: check license"""
   """Returns a bytestring version of 's', encoded as specified in 'encoding'.

   If strings_only is True, don't convert (some) non-string-like objects. 
   """
   if not isinstance(s, basestring):
      try:
         return str(s)
      except UnicodeEncodeError: 
         return unicode(s).encode(encoding, errors)
   elif isinstance(s, unicode):
      return s.encode(encoding, errors)
   elif s and encoding != 'utf-8': 
      return s.decode('utf-8', errors).encode(encoding, errors) 
   else: 
      return s 

def merge_dict(a, b):
   """Return a hash containing all the keys and vals of a and all
   those of b that don't clash with a.  Modifies a in place and also
   returns a"""
   for k in b.keys():
      if a.has_key(k): continue
      else: a[k] = b[k]
   return a

def dict_val(dict, key):
   "Returns dict[key], but if key isn't present, returns a blank string"
   try:
      return dict[key]
   except KeyError:
      return ''

def write_file(dir, fname, string):
   "Opens a fname in dir for writing, writes string, closes fname"
   with open(os.path.join(dir, fname),"w") as FILE:
      FILE.write(string)

def write_add(output_dir, output_fname, contents):
   """Do a write_file and add to list of generated files"""
   write_file(output_dir, output_fname, contents)
   generated.append(os.path.join(output_dir, output_fname))

def interpolate(template, vals):
   "apply the keys and values in vals to template, return filled-in template"
   try:
      print template_vars['base_href']
   except:
      pass

   manager = htmltmpl.TemplateManager()
   template = manager.prepare(template)
   tp = htmltmpl.TemplateProcessor(html_escape=0)
   for key in vals:
      try:
         if isinstance(vals[key], basestring):
            tp.set(key, smart_str(vals[key], encoding='ascii', errors='ignore'))
         elif vals[key]:
            tp.set(key, vals[key])

      except:
         pass
   return tp.process(template)

def tidy2xhtml(instr):
   pass
   #options = dict(output_xhtml=1,
   #               add_xml_decl=0,
   #               indent=1
   #               )
   #tidied = tidy.parseString(instr, **options)
   #return tidied


def make_static(output_dir, output_fname, template_fname, template_vars):
   template_fname = os.path.join(TEMPLATE_DIR, template_fname)
   try:
      os.unlink(template_fname + "c")
   except:
      pass
   write_add(output_dir, output_fname, interpolate(template_fname, template_vars))

def make_page(name):
   "Make a standard page in the httproot"
   make_static(OUTPUT_DIR, "%s.html" % name, "%s.tmpl" % name, opt)
class Msg:
   """Rudimentary class to store a message object that can save
   messages and then return them as html or text."""
   txt=[]
   web = False
   def __init__(self, web=web):
      self.txt = []
      self.web = web
   def add(self, text):
      self.txt.append(text)
      if not self.web:
         print text
   def out(self):
      if web:
         self.html()
      else:
         self.text()
   def html(self):
      return "<br />\n".join(self.txt)
   def text(self):
      return "\n".join(self.txt)
   def para(status="start"):
      if para == "start":
         self.add("<p>")
      else:
         self.add("</p>")
############################################################
class Planet():
   def __init__(self, *args, **kwargs):
      if 'direc' in kwargs:
         with berkeley_db('planets') as db:
            self.load_json(db[kwargs['direc']])
      elif isinstance(args[0], basestring):
         self.load_json(args[0])
      elif isinstance(args[0], dict):
         self.load_dict(args[0])
      else:
         self.load_dict(kwargs)

   def load_dict(self, h):
      if 'version' in h and h['version'] != DATA_FORMAT_VERSION:
         sys.stderr.write("Planet data file is version %s.  This is planeteria version %s.  Please upgrade or downgrade to match versions.\n" %
                          (h['version'], DATA_FORMAT_VERSION))
         sys.exit(-1)
      self.direc = h['direc']
      self.name = h['name']
      self.user = h['user']
      self.email = h['email']
      self.password = h['password']
      if 'last_downloaded' in h:
         self.last_downloaded = h['last_downloaded'] or 0
      else:
         self.last_downloaded = 0
      if 'sidebar' in h:
         self.sidebar = h['sidebar']
      else:
         self.sidebar = ''
         
      #self.feeds = [Feed(url=f) for f in h['feeds']]
      #print self.feeds[0].dump()
      self.feeds = h['feeds']

   def add_feed(self, feed):
      self.last_updated = 0
      self.feeds.append(feed)

   def load_json(self, j):
      self.load_dict(json.loads(j))

   def save(self):
      with berkeley_db('planets') as db:
         db[self.direc] = self.json()
 
   def serializable(self):
      return {'direc':self.direc,
              'name':self.name,
              'user':self.user,
              'email':self.email,
              'password':self.password,
              'feeds':self.feeds,
              'last_downloaded': self.last_downloaded,
              'sidebar':self.sidebar,
              'version':DATA_FORMAT_VERSION}
   def json(self):
      return json.dumps(self.serializable(), sort_keys=True, indent=3)

   def update_feed(self, url):
      """Download feed if it's out of date"""
      if not opt['force_check'] and time.time() < self.last_downloaded + CHECK_INTERVAL:
         return
      try:
         new_data = urlopen(url).read()
      except:
         raise
         return

      new_data = smart_str(new_data, encoding='ascii', errors='ignore')
      self.last_downloaded = time.time()

      with berkeley_db('cache') as db:
         try:
            cache = db[url]
         except KeyError:
            cache = ''

         if new_data != cache:
            db[url] = new_data
            print "Updating %s" % url

   def update(self):
      if not opt['force_check'] and time.time() < self.last_downloaded + CHECK_INTERVAL:
         return
      print "Updating %s." % self.direc
      for f in self.feeds:
         self.update_feed(f)
      self.last_downloaded = time.time()
      self.save()

   def generate(self):
      output_dir = os.path.join(OUTPUT_DIR, self.direc)
      print "Generating %s" % output_dir

      lopt = {'owner_name':self.user,
              'title':self.name,
              'feed_url':"%s%s/atom.xml" % (BASE_HREF, self.direc),
              'opml_url':"%s%s/opml.xml" % (BASE_HREF, self.direc),
              'feed_page':"%s%s/" % (BASE_HREF, self.direc),
              'updated':time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(self.last_downloaded)),
              'date':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
              'datemodified':time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(self.last_downloaded)),
              }

      ## Get the entries and sort them
      entries = {}
      lopt['Feeds']=[]
      for url, f in self.feeds.items():
         with berkeley_db('cache') as db:
            cache = db[url]

         parsed = feedparser.parse(cache)
         if (len(parsed.entries) == 0 and parsed.bozo and 
             str(parsed.bozo_exception).startswith("'ascii' codec can't encode character")):
            parsed = feedparser.parse(smart_str(self.data, encoding='ascii', errors='ignore'))

         for e in parsed.entries:
            e['links'] = parsed['feed']['links']
            e['feed_name'] = smart_str(parsed['feed']['title'], encoding='ascii', errors='ignore')
            e['channel_title_plain'] = e['feed_name']
            e['channel_faceurl'] = f['image']
            e['channel_name'] = e['feed_name']
            e['subtitle'] = parsed['feed']['subtitle']
            e['feed_id'] = parsed['feed']['link']
            entries[e['id']] = e

         ## OPML template stuff and sidebar stuff
         feed_data = {}
         for l in parsed['feed']['links']:
            if l['rel']=="self":
               feed_data['url'] = l['href']
            elif l['rel']=="alternate":
               feed_data['link'] = l['href']

         feed_data['author'] = f['name']
         feed_data['title'] = smart_str(parsed['feed']['title'], encoding='ascii', errors='ignore')
         lopt['Feeds'].append(feed_data)

      sorted_entries = sorted(entries.values(), reverse=True, 
                              key=parse_updated_time)

         
      for e in sorted_entries[:50]:
         e['content_encoded'] = e['content'][0]['value']
         #e['content'] = html2xml(just_body(tidy2xhtml(e['content'][0]['value'])))
         try:
            u = time.strptime(e['updated'], "%a, %d %b %Y %H:%M:%S +0000")
         except ValueError:
            u = [0,0,0,0,0,0,0,0,0]
         try:
            e['date'] =  time.strftime("%Y-%m-%dT%H:%M:%SZ", u)
         except ValueError:
            e['date'] =  "1900-01-01T00:00:00Z"
         try:
            e['updated'] =  time.strftime("%Y-%m-%dT%H:%M:%SZ", u)
         except ValueError:
            e['updated'] =  "1900-01-01T00:00:00Z"
         
      lopt['Items'] = sorted_entries[:50]
      mopt = dict(lopt.items()+opt.items() + self.__dict__.items())

      # generate page
      make_static(output_dir, "index.html", "index.html.tmpl", mopt)
      make_static(output_dir, "atom.xml", "atom.xml.tmpl", mopt)
      make_static(output_dir, "opml.xml", "opml.xml.tmpl", mopt)

   def del_feed(self, url):
      d = None
      for i in range(len(self.feeds)):
         if self.feeds[i].url == url:
            d = i
            break
      if d:
         del self.feeds[d]
      else:
         sys.stderr.write("Couldn't find feed %s\n" % url)

   def dump(self):
      print self.json()

###############################################################################
class Galaxy(list):
   "A collection of planets"

   selected = None

   def __init__(self, selected=None):
      self.planets = []
      if selected: self.selected = selected

   def append(self, planet):
      """planet is a Planet object"""
      self.planets.append(planet)

   def load(self):
      p = []
      with berkeley_db('planets') as db:
         for k in db.keys():
            if not self.selected or k in self.selected:
               self.append(Planet(db[k]))

   def dump(self):
      for p in self.planets:
         p.dump()

   def save(self):
      for p in self.planets:
         p.save()

   def update(self):
      for p in self.planets:
         p.update()

   def generate(self):
      for p in self.planets:
         p.generate()
###############################################################################
#
# ADMIN
#
sys.path.insert(0,"..")

#######################
##
## Utility Functions
##
########################

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

    for feed in planet.feeds:
        ret = (ret + "      new_feed('%s', '%s', '%s', '%s', '%s', '%s', '%s');\n" 
               % (feed.url,
                  feed.url,
                  feed.name,
                  '',
                  feed.image[planet.direc],
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

## Setup and globals
VERSION = "0.2";
Form=''

def update_planet(planet):
    p = Planet(planet)
    p.update()
    p.generate()


def do_admin():
    try:
        planet_dir = os.sep.join(os.environ['SCRIPT_FILENAME'].split(os.sep)[:-1])
    except KeyError:
        try:
            planet_dir = os.sep.join((os.getcwd() + os.environ['SCRIPT_NAME']).split(os.sep)[:-1])
        except:
            planet_dir = os.getcwd()
        
    opt['planet_subdir'] = planet_dir.split(os.sep)[-1]
    output_dir = planet_dir

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

    planet = Planet(direc=opt['planet_subdir'])

    ## Template
    print interpolate(os.path.join(opt['template_dir'], 'admin.tmpl'), template_vars(planet, Form))


###############################################################################
# 
# New Planet
#
errm=Msg()

def template_vars(subdir="", email=""):
    "Returns a dict with the template vars in it"
    doc=opt.copy()
    
    doc['subdirectory'] = subdir
    doc['owner_email'] = email
    doc['error'] = errm.html()
    return doc

def validate_input(subdir):

    if subdir == "":
        return False

    valid = True

    if re.search('\\W', subdir):
        errm.add("Subdirectory can only contain letters, numbers and underscores.")
        valie = False

    return valid

def make_planet(subdir):

    path = os.path.join(opt['OUTPUT_DIR'], subdir)

    try:
        shutil.copytree(opt['new_planet_dir'], path, symlinks=True)
    except(OSError), errstr:
        if os.path.exists(path):
            errm.add("%s already exists. Please choose another subdirectory name." % subdir)
            return False
        errm.add("Couldn't create planet: %s" % errstr)
        return False

    p = Planet({'direc':subdir,
                'name':'Planet %s' % subdir,
                'user':'',
                'email':'',
                'password':'passme',
                'feeds':{'http://hackervisions.org/?feed=rss2':{'image':'http://www.softwarefreedom.org/img/staff/vasile.jpg','name':'James Vasile', 'url':'http://hackervisions.org/?feed=rss2'}}
                })
    
    p.save()
    mopt = dict(opt.items()+p.__dict__.items())

    make_static(path, "index.html", "welcome.tmpl", mopt)
    return True

def do_new_planet():
    global Form
    Form = cgi.FieldStorage()

    subdir = Form.getvalue("subdirectory", '').lower()
    #email = Form.getvalue("owner_email", '')

    if validate_input(subdir):
        if make_planet(subdir):
            print "Location: http://%s/%s/admin.py\n\n" % (opt['domain'], subdir)
            return
    print "Content-type: text/html\n\n" 
    print interpolate(os.path.join(opt['template_dir'], 'new.tmpl'), template_vars(subdir))


def static():
    "Return a static version of this page suitable for caching"
    global Form
    Form = cgi.FieldStorage()
    return interpolate(template_fname, template_vars())

###############################################################################

if __name__ == "__main__":

   parse_options()

   # we're either admin or new planet
   do_new_planet()
