from util import berkeley_db
from planet import Planet

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


   def delete_missing_planets(self):
      for p in self.planets:
         p.delete_if_missing()
