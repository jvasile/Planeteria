from util import our_db
from planet import Planet
import logging
log = logging.getLogger('planeteria')

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
      with our_db('planets') as db:
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

   def delete_unused_feeds(self):
      planets = []
      with our_db('planets') as db:
         for k in db.keys():
            planets.append(Planet(db[k]))

      feed_urls = {}
      for p in planets:
         for f in p.feeds:
            feed_urls[f] = f

      feed_urls = feed_urls.keys()
      with our_db('cache') as db:
         for k in db.keys():
            if not k in feed_urls:
               del db[k]
               log.debug("Removed %s from cache." % k)
         
   def delete_missing_planets(self):
      for p in self.planets:
         p.delete_if_missing()

   def get_planet_by_subdir(self, subdir):
      for p in self.planets:
         if p.direc == subdir:
            return p
      return None
