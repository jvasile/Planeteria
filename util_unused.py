#!/usr/bin/python
"""
Planeteria unused utility functions
Copyright 2009-2013 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

Utility functions saved in case they come in handy later
"""

import htmltmpl # Debian package python-htmltmpl

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
