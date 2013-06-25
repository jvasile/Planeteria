#!/usr/bin/python
"""
Planeteria util functions
Copyright 2009-2013 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

Utility functions
"""

import os, sys, dbm, time, shelve
import config as cfg
from config import opt
import logging
log = logging.getLogger('planeteria')
import dateutil.parser
import withsqlite

try:
   import tidy
except KeyError:
   if not 'PATH' in os.environ:
      os.environ['PATH'] = ''
      import tidy
except (OSError, ImportError):
   import tidylib as tidy

generated=[]

def pretty_print_dict (d, indent=0):
   for key, value in d.iteritems():
      print '\t' * indent + str(key)
      if isinstance(value, dict):
         pretty_print_dict(value, indent+1)
      else:
         print '\t' * (indent+1) + str(value)

def html2xml(ins):
   'replace all the html entities with xml equivs'
   ins = str(ins).replace("&nbsp;", "&#160;")
   return ins

def parse_updated_time(entry):
   return str(entry['updated'])
   
class sqlite_db(withsqlite.sqlite_db):
   def __init__(self, fname):
      withsqlite.sqlite_db.__init__(self, os.path.join(cfg.data_dir, fname))

class shelve_db:
   def __init__(self, fname):
      self.fname = fname + ".shelf"
   def __enter__(self):
      self.db = shelve.open(os.path.join(cfg.data_dir, self.fname), 'c', writeback=False)
      return self.db
   def __exit__(self, type, value, traceback):
      self.db.close()

class our_db(sqlite_db):
   pass

class berkeley_db:
   def __init__(self, fname):
      self.fname = fname
   def __enter__(self):
      self.db = dbm.open(os.path.join(cfg.data_dir, self.fname), 'c')
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

def dict_val(dic, key):
   "Returns dic[key], but if key isn't present, returns a blank string"
   try:
      return dic[key]
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

def strip_body_tags(text):
   text = text.strip()
   if text.startswith('<body>'):
      text =  text[6:]
   if text.endswith('</body>'):
      text = text[:-7]
   return text.strip()

def lxml_tidy(instr, xml=False):
   from lxml import etree
   if instr == "":
      return ''
   tree  = etree.HTML(instr.replace('\r', ''))
   if tree is None:
      return ''
   output_text = '\n'.join([ etree.tostring(stree, pretty_print=True, method= "xml" if xml else "html") 
                             for stree in tree ])
   return str(output_text)

def soup_tidy(instr):
   from BeautifulSoup import BeautifulSoup
   tree = BeautifulSoup(instr)
   good_html = tree.prettify()
   return str(good_html)

def html_tidy(instr):
   """We can't really use this because html_tidy pukes on unknown tags
   and rss feeds contain all kinds of crazy stuff.

   Maybe we could play with force_output=1 and figure out which tags
   are odd and then add them to new-blocklevel-tags, new-empty-tags,
   new-inline-tags, and new-pre-tags, but that would be a ton of iffy
   work.

   And we don't really need tidy html, do we?
   """
   return "Don't use html_tidy."
   options = dict(output_xhtml=1,
                  add_xml_decl=0,
                  indent=1,
                  show_body_only=1,
                  )
   tidied = tidy.parseString(instr, **options)
   return str(tidied)


def tidy2html(instr, xml=False):
   if not instr:
      return ''
   return lxml_tidy(instr, xml)
   #return soup_tidy(lxml_tidy(html_tidy(instr)))


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
