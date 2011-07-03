#!/usr/bin/env python

"""
Planeteria rewrite.
Copyright James Vasile 2011
Released under the GNU Affero General Public License, version 3 or later.
"""

"""
Back End
  generates the various pages

Front End
  admin to various pages
"""

import os, sys
from optparse import OptionParser
import config
from config import *
log = logging.getLogger('planeteria')
from galaxy import Galaxy
from planet import Planet

if not os.path.exists(DATA_DIR):
   os.mkdir(DATA_DIR)

planets = []

def parse_options():
   parser = OptionParser()
   parser.add_option("", "--force", action="store_true", dest="force_update", help="force update of feeds", default=False),
   parser.add_option("", "--no-update", action="store_true", dest="no_update", help="prevent feed updates", default=False),
   parser.add_option('', '--delete-missing', dest="delete_missing", help="delete planets from db if they are not in file system", action="store_true", default=False)
   parser.add_option('', '--clean', dest="clean", help="remove missing planets, unused feeds", action="store_true", default=False)
   (options, args) = parser.parse_args()

   opt['force_check'] = options.force_update
   opt['no_update'] = options.no_update

   if len(args) >= 1:
      global planets
      planets.extend(args)

   if options.clean:
      log.debug("Cleaning databse.")
      galaxy = Galaxy(planets)
      galaxy.load()
      galaxy.delete_missing_planets()
      galaxy.delete_unused_feeds()
   elif options.delete_missing:
      log.debug("Deleting missing planets.")
      galaxy = Galaxy(planets)
      galaxy.load()
      galaxy.delete_missing_planets()
   else:
      return

   sys.exit()

if __name__ == "__main__":

   parse_options()


   import templates
   for p,t in {'copyright':templates.Copyright,
               'thanks':templates.Thanks,
               'tos':templates.TOS,
               'index':templates.Main_Page,
               }.items():
      t(opt).write(OUTPUT_DIR, "%s.html" % p)
   galaxy = Galaxy(planets)
   galaxy.load()
   #galaxy.dump()
   if not opt['no_update']:
      galaxy.update()
   galaxy.generate()

