import sys, time
from config import *
log = logging.getLogger('planeteria')
import feedparser
import simplejson as json
from urllib import urlopen
from util import smart_str, parse_updated_time, berkeley_db, write_file, html2xml, just_body, tidy2xhtml
import templates
import dateutil.parser

def to_json(python_object):
   if isinstance(python_object, time.struct_time):
      return {'__class__': 'time.asctime',
              '__value__': time.asctime(python_object)}

   if isinstance(python_object, feedparser.CharacterEncodingOverride):
      return {'__class__': 'basestring',
              '__value__': str(python_object)}
   raise TypeError(repr(python_object) + ' is not JSON serializable')

def serialize_feedparse(parse_object):
   return json.dumps(parse_object, default=to_json)

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
      self.load_dict(json.loads(j))

   def save(self, update_config_timestamp=False, ignore_missing_dir=False):
      output_dir = os.path.join(OUTPUT_DIR, self.direc)
      if not ignore_missing_dir and not os.path.exists(output_dir):
         log.info("Can't find %s directory.  Skipping save." % output_dir)
         return

      log.debug("Saving the planet! %s" %  self.direc)
      if update_config_timestamp:
         self.last_config_change = time.time()
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
              'last_config_change':self.last_config_change,
              'version':DATA_FORMAT_VERSION}
   def json(self):
      return json.dumps(self.serializable(), sort_keys=True, indent=3)

   def update_feed(self, url):
      with berkeley_db('cache') as db:
         try:
            cache = json.loads(db[url])
         except KeyError:
            log.info("Can't find %s in cache.  Making default." % url)
            cache = {'data':'', 'last_downloaded':0, 'dload_fail':False}

      """Download feed if it's out of date"""
      if not opt['force_check'] and time.time() < cache['last_downloaded'] + CHECK_INTERVAL:
         log.debug("Cache is fresh.  Not downloading %s." % url)
         return
      try:
         log.debug("Reading %s" % url)
         import feedparser
         parsed = feedparser.parse(url.strip())
         cache['dload_fail'] = False
      except:
         cache['dload_fail']=True
         with berkeley_db('cache') as db:
            db[url] = json.dumps(cache, sort_keys=True, indent=3)
         return

      if parsed and parsed.entries: cache['data'] = parsed
      cache['last_downloaded'] = time.time()
      with berkeley_db('cache') as db:
         try:
            db[url] = json.dumps(cache, default=to_json, sort_keys=True, indent=3)
         except TypeError, e:
            log.debug("Can't save feed (%s): %s" % (url, e))
            return
         log.debug("Saved downloaded feed for %s" % url)

   def update(self):
      output_dir = os.path.join(OUTPUT_DIR, self.direc)
      if not os.path.exists(output_dir):
         log.info("Can't find %s directory.  Skipping update." % output_dir)
         return
      print "Updating %s." % self.direc
      for f in self.feeds:
         self.update_feed(f)
      self.last_downloaded = time.time()
      self.save()

   def generate(self):
      output_dir = os.path.join(OUTPUT_DIR, self.direc)
      if not os.path.exists(output_dir):
         log.info("Can't find %s directory.  Skipping generate." % output_dir)
         return
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
            if not url in db:
               continue
            cache = json.loads(db[url])
         parsed = cache['data']
         if not parsed or not parsed['entries']:
            log.debug("No data for %s.  Skipping." % url)
            continue
         
         #import chardet
         for e in parsed['entries']:
            e['links'] = parsed['feed']['links']
            e['feed_name'] = smart_str(parsed['feed']['title'], encoding='ascii', errors='ignore')
            e['channel_title_plain'] = e['feed_name']
            e['channel_image'] = f['image']
            e['channel_name'] = e['feed_name']
            if 'subtitle' in parsed['feed']:
               e['subtitle'] = parsed['feed']['subtitle']
            else:
               e['subtitle']=''
            e['channel_link'] = e['feed_id'] = parsed['feed']['link']
            e['date'] = dateutil.parser.parse(e['updated'])
            e['updated'] = e['date']
            if not 'id' in e: e['id'] = e['link']
            if not 'link' in e: e['link'] = e['id']
            if not e['id'] and not e['link']:
               log.debug('%s has neither id nor link' % e['feed_name'])
            entries[e['id']] = e

         ## OPML template stuff and sidebar stuff
         feed_data = {}
         for l in parsed['feed']['links']:
            if not 'type' in l:
               l['type']='text/html'
            if l['rel']=="self":
               feed_data['url'] = l['href']
            elif l['rel']=="alternate":
               if 'href' in l:
                  feed_data['link'] = l['href']
         feed_data['author'] = f['name']
         feed_data['title'] = smart_str(parsed['feed']['title'], encoding='ascii', errors='ignore')
         feed_data['image'] = f['image']
         feed_data['url'] = f['url']
         lopt['Feeds'].append(feed_data)

      sorted_entries = sorted(entries.values(), reverse=True, 
                              key=parse_updated_time)

      for e in sorted_entries[:50]:
         if not 'content' in e:
            e['content_encoded'] = html2xml(tidy2xhtml(e['summary']))
         else:
            e['content_encoded'] = html2xml(tidy2xhtml(e['content'][0]['value']))

         if not 'summary' in e:
            e['summary'] = e['content'][0]['value']
         e['summary_encoded'] = html2xml(tidy2xhtml(e['summary']))

      lopt['Items'] = sorted_entries[:50]
      mopt = dict(lopt.items()+opt.items() + self.__dict__.items())

      # generate pages
      templates.OPML(mopt).write(output_dir, "opml.xml")
      templates.Atom(mopt).write(output_dir, "atom.xml")
      templates.Planet_Page(mopt).write(output_dir, "index.html")

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
               self.feeds[url]['url'] = url
               if name: self.feeds[url]['name'] = name
            else:
               self.feeds[url]={'url':url, 'name':name, 'image':''}

   def dump(self):
      print self.json()

   def dump_cache(self):
      for url in self.feeds:
         print url
         with berkeley_db('cache') as db:
            cache = db[url]
         try:
            cache = json.loads(cache)
         except json.decoder.JSONDecodeError:
            return
         
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

