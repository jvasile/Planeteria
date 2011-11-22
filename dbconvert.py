#!/usr/bin/python

# convert from shelf to sqlite

import sys
from util import our_db, sqlite_db
import simplejson as json

with sqlite_db('planets') as sdb:
   sdb.clear()
   with our_db('planets') as odb:
      for key, val in odb.items():
         val = json.loads(val)
         sdb[key]=val
sys.exit()
with sqlite_db('cache') as sdb:
   sdb.clear()
   with our_db('cache') as odb:
      for key, val in odb.items():
         val = json.loads(val)
         sdb[key]=val

