import sys, time
from config import *
log = logging.getLogger('planeteria')
import feedparser
import simplejson as json
from urllib import urlopen
from util import smart_str, parse_updated_time, berkeley_db, write_file, html2xml, just_body, tidy2xhtml
import templates
import dateutil.parser

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

   def add_feed(self, feed):
      self.last_updated = 0
      self.feeds.append(feed)

   def load_json(self, j):
      self.load_dict(json.loads(j))


   def save(self, update_config_timestamp=False):
      if update_config_timestamp:
         self.last_config_change = time.time()
      with berkeley_db('planets') as db:
         db[self.direc] = self.json()

      log.debug(self.json())

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
            if not url in db:
               continue
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
            e['channel_link'] = e['feed_id'] = parsed['feed']['link']
            e['date'] = dateutil.parser.parse(e['updated'])
            e['updated'] = e['date']
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
         feed_data['image'] = f['image']
         feed_data['url'] = f['url']
         lopt['Feeds'].append(feed_data)

      sorted_entries = sorted(entries.values(), reverse=True, 
                              key=parse_updated_time)
         
      for e in sorted_entries[:50]:
         if not 'content' in e:
            e['content'] = e['summary']
            e['content_encoded'] = e['summary']
         else:
            e['content_encoded'] = e['content'][0]['value']
            e['content'] = html2xml(just_body(tidy2xhtml(e['content'][0]['value'])))

         print e['updated']
         if not 'summary' in e:
            e['summary'] = ''#e['content']

      lopt['Items'] = sorted_entries[:50]
      mopt = dict(lopt.items()+opt.items() + self.__dict__.items())

      # generate pages
      templates.OPML(mopt).write(output_dir, "opml.xml")
      templates.Atom(mopt).write(output_dir, "atom.xml")
      templates.Planet_Page(mopt).write(output_dir, "index.html")

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

