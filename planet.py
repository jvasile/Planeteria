#!/usr/bin/python

import os, sys, time, shutil, datetime
import config as cfg
from config import opt
import logging
log = logging.getLogger('planeteria')
import feedparser
try:
   import simplejson as json
except ImportError:
   import json
from urllib import urlopen
from util import smart_str, parse_updated_time, our_db, write_file, html2xml
import util as u
import templates
import dateutil.parser


def to_json(python_object):
   if isinstance(python_object, time.struct_time):
      return {'__class__': 'time.asctime',
              '__value__': time.asctime(python_object)}

   #if isinstance(python_object, feedparser.CharacterEncodingOverride):
   #   return {'__class__': 'basestring',
   #           '__value__': str(python_object)}

   return {'__class__': 'basestring',
           '__value__': str(python_object)}

   #raise TypeError(repr(python_object) + ' is not JSON serializable')

class Planet():
   def __init__(self, *args, **kwargs):
      if 'direc' in kwargs:
         with our_db('planets') as db:
            self.load_dict(db[kwargs['direc']])
      elif isinstance(args[0], basestring):
         self.load_json(args[0])
      elif isinstance(args[0], dict):
         self.load_dict(args[0])
      else:
         self.load_dict(kwargs)

   def load_dict(self, h):
      if 'version' in h and h['version'] != cfg.DATA_FORMAT_VERSION:
         sys.stderr.write("Planet data file is version %s.  This is planeteria version %s.  Please upgrade or downgrade to match versions.\n" %
                          (h['version'], cfg.DATA_FORMAT_VERSION))
         sys.exit(-1)
      self.direc = h['direc']
      self.name = h['name']
      self.user = h['user']
      self.email = h['email']
      self.password = h['password']
      if 'last_downloaded' in h:
         self.last_downloaded = h['last_downloaded'] or 1
      else:
         self.last_downloaded = 0
      if 'sidebar' in h:
         self.sidebar = h['sidebar']
      else:
         self.sidebar = ''

      try:
         self.last_config_change = h['last_config_change']
      except KeyError:
         self.last_config_change = 1
         
      #self.feeds = [Feed(url=f) for f in h['feeds']]
      #print self.feeds[0].dump()
      self.feeds = h['feeds']


   def load_json(self, j):
      j = unicode(j, errors='replace')
      self.load_dict(json.loads(j, strict=False))

   def save_cache(self, cache, url):
      with our_db('cache') as db:
         #db[url.encode("utf-8")] = cache
         db[url] = cache

   def save(self, update_config_timestamp=False, ignore_missing_dir=False):
      output_dir = os.path.join(cfg.OUTPUT_DIR, self.direc)
      if not ignore_missing_dir and not os.path.exists(output_dir):
         log.info("Can't find %s directory.  Skipping save." % output_dir)
         return

      log.debug("Saving the planet! %s" %  self.direc)
      if update_config_timestamp:
         self.last_config_change = time.time()
      with our_db('planets') as db:
         #db[self.direc.encode("utf-8")] = self.serializable()
         db[self.direc] = self.serializable()

   def serializable(self):
      return {'direc':self.direc,
              'name':self.name,
              'user':self.user,
              'email':self.email,
              'password':self.password,
              'feeds':self.feeds,
              'last_downloaded': self.last_downloaded,
              'sidebar':self.sidebar,
              'last_config_change':self.last_config_change,
              'version':cfg.DATA_FORMAT_VERSION}
   def json(self):
      return json.dumps(self.serializable(), sort_keys=True, indent=3)

   def update_feed(self, url):
      """Download feed if it's out of date"""

      force_check = opt['force_check']
      with our_db('cache') as db:
         try:
            cache = db[url]
         except KeyError:
            log.info("Can't find %s in cache.  Making default." % url)
            cache = {'data':'', 'last_downloaded':0, 'dload_fail':False}
            force_check = True
         except json.decoder.JSONDecodeError, e:
            log.debug("Json error on updating url %s: %s" % (url, e))
            cache = {'data':'', 'last_downloaded':0, 'dload_fail':False}
            force_check = True

      if not opt['force_check'] and time.time() < cache['last_downloaded'] + cfg.CHECK_INTERVAL:
         log.debug("Cache is fresh.  Not downloading %s." % url)
         return
      try:
         log.debug("Reading %s" % url)
         parsed = feedparser.parse(url.strip())
         cache['dload_fail'] = False
      except:
         cache['dload_fail']=True
         self.save_cache(cache, url)
         return

      if parsed and parsed.entries:
         cache['data'] = parsed

      cache['last_downloaded'] = time.time()
      with our_db('cache') as db:
         try:
            #db[url.encode("utf8")] = cache
            db[url] = cache
         except TypeError, e:
            log.debug("Can't save feed (%s): %s" % (url, e))
            cache['error'] = str(e)
            self.save_cache(cache, url)
            return
         log.debug("Saved downloaded feed for %s" % url)

   def update(self):
      output_dir = os.path.join(cfg.OUTPUT_DIR, self.direc)
      if not os.path.exists(output_dir):
         log.info("Can't find %s directory.  Skipping update." % output_dir)
         return
      print "Updating %s." % self.direc
      for f in self.feeds:
         self.update_feed(f)
      self.last_downloaded = time.time()
      self.save()

   def generate(self):
      output_dir = os.path.join(cfg.OUTPUT_DIR, self.direc)
      if not os.path.exists(output_dir):
         log.info("Can't find %s directory.  Skipping generate." % output_dir)
         return
      print "Generating %s" % output_dir
      lopt = {'owner_name':self.user,
              'owner_email':self.email,
              'title':self.name,
              'feed_url':"%s%s/atom.xml" % (cfg.BASE_HREF, self.direc),
              'opml_url':"%s%s/opml.xml" % (cfg.BASE_HREF, self.direc),
              'feed_page':"%s%s/" % (cfg.BASE_HREF, self.direc),
              'updated':time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(self.last_downloaded)),
              'date':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
              'datemodified':time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(self.last_downloaded)),
              }

      ## Get the entries and sort them
      entries = {}
      lopt['Feeds']=[]
      for url, f in self.feeds.items():
         with our_db('cache') as db:
            if not url in db:
               continue
            try:
               cache = db[url]
            except json.decoder.JSONDecodeError, e:
               log.debug("Json error on generating url %s: %s" % (url, e))
               continue

         parsed = cache['data']
         if not parsed or not parsed['entries']:
            log.debug("No data for %s.  Skipping." % url)
            continue
         
         for e in parsed['entries']:
            e['name'] = f['name']
            if 'links' in parsed['feed']:
               e['links'] = parsed['feed']['links']
            else:
               e['links'] = []
            if 'title' in parsed['feed']:
               e['feed_name'] = smart_str(parsed['feed']['title'], encoding='ascii', errors='ignore')
            else:
               e['feed_name'] = f['name']
            e['channel_title_plain'] = e['feed_name']
            e['channel_image'] = f['image']
            e['channel_name'] = e['feed_name']
            if 'subtitle' in parsed['feed']:
               e['subtitle'] = parsed['feed']['subtitle']
            else:
               e['subtitle']=''
            if 'link' in parsed['feed']:
               if parsed['feed']['link'].endswith('/'):
                  e['channel_link'] = e['feed_id'] = parsed['feed']['link']
               else:
                  e['channel_link'] = e['feed_id'] = parsed['feed']['link']+'/'
            else:
               e['channel_link'] = e['feed_id'] = f['feedurl']
            if 'updated' in e:
               e['date'] = dateutil.parser.parse(e['updated']).strftime("%Y-%m-%d %H:%M:%S")
               e['updated'] = dateutil.parser.parse(e['updated']).isoformat()
            elif 'published_parsed' in e:
               if len(e['published_parsed']) == 9:
                  e['date'] = time.strftime("%Y-%m-%d %H:%M:%S", e['published_parsed'])
                  e['updated'] = datetime.date.fromtimestamp(time.mktime(e['published_parsed'])).isoformat()
               else:
                  e['date'] = dateutil.parser.parse(e['published_parsed']['__value__']).strftime("%Y-%m-%d %H:%M:%S")
                  e['updated'] = dateutil.parser.parse(e['published_parsed']['__value__']).isoformat()
            else:
               e['date'] = e['updated'] = '1970-01-01T00:00:00Z'
               # We really should assume the blog post is from when it is first seen for lack of a better option
               #e['date'] = e['updated'] = datetime.now().strftime("%Y-%m-%dT%H:00Z")
               log.debug("No updated or date field in entry for %s" % url)
               #pretty_print_dict(e)
            if not 'id' in e: e['id'] = e['link']
            if not 'link' in e: e['link'] = e['id']
            if not e['id'] and not e['link']:
               log.debug('%s has neither id nor link' % e['feed_name'])
            entries[e['id']] = e

         ## OPML template stuff and sidebar stuff
         feed_data = {}

         # Default these to the feed itself
         if 'feedurl' in f:
            feed_data['url'] = f['feedurl']
            feed_data['link'] = f['feedurl']

         for l in e['links']:
            if not 'type' in l:
               l['type']='text/html'
            if l['rel']=="self":
               feed_data['url'] = l['href']
            elif l['rel']=="alternate":
               if 'href' in l:
                  feed_data['link'] = l['href']
         feed_data['author'] = f['name']
         if 'title' in parsed['feed']:
            feed_data['title'] = smart_str(parsed['feed']['title'], encoding='ascii', errors='ignore')
         else:
            feed_data['title'] = f['name']
         feed_data['image'] = f['image']
         if 'feedurl' in f:
            feed_data['url'] = f['feedurl']
         else:
            log.error("%s is missing the feedurl key.  Falling back to url" % url)
            feed_data['url'] = f['url']
         lopt['Feeds'].append(feed_data)

      sorted_entries = sorted(entries.values(), reverse=True, 
                              key=parse_updated_time)

      for e in sorted_entries[:50]:
         if 'summary' in e and not 'content' in e:
            e['content_encoded'] = u.strip_body_tags(html2xml(u.tidy2html(e['summary'])).strip())
         elif e['content'][0]['value']:
            e['content_encoded'] = u.strip_body_tags(html2xml(u.tidy2html(e['content'][0]['value'])).strip())
         else:
            e['summary_encoded'] = 'N/A'
            e['content_encoded'] = 'N/A'
            continue

         if not 'summary' in e:
            e['summary'] = e['content'][0]['value']
         e['summary_encoded'] = u.strip_body_tags(html2xml(u.tidy2html(e['summary'])).strip())

         
      lopt['Items'] = sorted_entries[:50]

      # now do it again for xml
      for e in sorted_entries[:50]:
         if not 'content' in e:
            e['content_encoded'] = u.strip_body_tags(html2xml(u.tidy2html(e['summary'], xml=True)).strip())
         elif e['content'][0]['value']:
            e['content_encoded'] = u.strip_body_tags(html2xml(u.tidy2html(e['content'][0]['value'], xml=True)).strip())
         else:
            e['summary_encoded'] = 'N/A'
            e['content_encoded'] = 'N/A'
            continue

         if not 'summary' in e:
            e['summary'] = e['content'][0]['value']
         e['summary_encoded'] = u.strip_body_tags(html2xml(u.tidy2html(e['summary'], xml=True)).strip())

      lopt['ItemsXML'] = sorted_entries[:50]

      mopt = dict(opt.items()+lopt.items() + self.__dict__.items()) 

      # generate pages
      templates.OPML(mopt).write(output_dir, "opml.xml")
      templates.Atom(mopt).write(output_dir, "atom.xml")
      templates.Planet_Page(mopt).write(output_dir, "index.html")
      templates.Snippet(mopt).write(output_dir, "snippet.html")

      for f in os.listdir(opt['new_planet_dir']):
         if f == "index.html":
            continue
         src = os.path.join(opt['new_planet_dir'], f)
         dst = os.path.join(output_dir, f)
         if not os.path.exists(dst):
            if os.path.islink(src):
               linkto = os.readlink(src)
               os.symlink(linkto, dst)
            else:
               shutil.copy(src, dst)

   def add_feed(self, url, name, image="", save=False):
      if not name: name = url
      t = {'feedurl':url, 
           'name':name,
           'image':image}
      self.feeds[url] = t
      if save:
         self.save()

   def del_feed(self, url):
      try:
         del self.feeds[url]
      except KeyError:
         sys.stderr.write("Couldn't find feed %s\n" % url)

   def import_opml(self, filespec):
      log.info("Importing %s into %s" % (filespec, self.direc))
      from xml.etree import ElementTree

      with open(filespec, 'rt') as f:
         tree = ElementTree.parse(f)

      for node in tree.getiterator('outline'):
         name = node.attrib.get('text')
         url = node.attrib.get('xmlUrl')

         if url:
            if url in self.feeds:
               self.feeds[url]['feedurl'] = url
               if name: self.feeds[url]['name'] = name
            else:
               self.feeds[url]={'feedurl':url, 'name':name, 'image':''}

   def delete(self):
      with our_db('planets') as db:
         del db[self.direc]
      try:
         shutil.rmtree(os.path.join(cfg.OUTPUT_DIR, self.direc))
      except OSError:
         pass
      log.info("Deleted planet: %s" % self.direc)

   def delete_if_missing(self):
      output_dir = os.path.join(cfg.OUTPUT_DIR, self.direc)
      if not os.path.exists(output_dir):
         self.delete()

   def dump(self):
      print self.json()

   def dump_cache(self):
      for url in self.feeds:
         print url
         with our_db('cache') as db:
            cache = db[url]
         
         print json.dumps(cache)

planets = []
def parse_options():
   from optparse import OptionParser
   parser = OptionParser()
   parser.add_option("-i", "--import", dest="import_opml", help="import opml FILE", metavar="FILE")
   parser.add_option("-d", "--dump", dest="dump_planet", help="dump planet", action="store_true", default=False)
   parser.add_option("-c", "--cache", dest="dump_planet_cache", help="dump planet's cache", action="store_true", default=False)

   (options, args) = parser.parse_args()

   if len(args) >= 1:
      global planets
      planets.extend(args)

   if options.dump_planet_cache:
      for p in planets:
         curr = Planet(direc=p)
         print curr.dump_cache()

   if options.dump_planet:
      for p in planets:
         curr = Planet(direc=p)
         print curr.dump()

   if options.import_opml:
      for p in planets:
         curr = Planet(direc=p)
         curr.import_opml(options.import_opml)
         
if __name__ == "__main__":
   parse_options()

