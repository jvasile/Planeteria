import unittest
from lxml import etree
from galaxy import Galaxy
from new_planet import make_planet
import feedvalidator, sys, os, urllib, urllib2, urlparse
from feedvalidator import compatibility

"""
Maybe this is the start of emitting valid xml in atom.xml and
opml.xml.  It would be nice to emit valid html in index.html too.

License note: this file includes code (lightly modified by James
Vasile in 2013) from the feedparser demo.  The license of the original
code is in the feedparser directory.

See http://feedvalidator.org/docs/ for help fixing validation errors.
"""

def get_validation_output(url, filter="AA"):
  # "A" is most basic level
  # "AA" mimics online validator
  # "AAA" is experimental; these rules WILL change or disappear in future version
  url = urlparse.urljoin('file:' + urllib.pathname2url(os.getcwd()) + '/', url)
  try:
    url = url.decode('utf-8').encode('idna')
  except:
    pass
  print 'Validating %s' % url

  curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
  basedir = urlparse.urljoin('file:' + curdir, ".")

  try:
    if url.startswith(basedir):
      events = feedvalidator.validateStream(urllib.urlopen(url), firstOccurrenceOnly=1,base=url.replace(basedir,"http://www.feedvalidator.org/"))['loggedEvents']
    else:
      events = feedvalidator.validateURL(url, firstOccurrenceOnly=1)['loggedEvents']
  except feedvalidator.logging.ValidationFailure, vf:
    events = [vf.event]

  filterFunc = getattr(compatibility, filter)
  events = filterFunc(events)

  from feedvalidator.formatter.text_plain import Formatter
  output = Formatter(events)
  if output:
      return "\n".join(output)
  else:
      return True

def validate_p(url, filter="AA"):
  # "A" is most basic level
  # "AA" mimics online validator
  # "AAA" is experimental; these rules WILL change or disappear in future versions
    v = get_validation_output(url, filter)
    if v == True:
        return True
    else:
        print v
        return False

class validate_test(unittest.TestCase):
    """Right now we're just testing the validate_p function, so we're
    testing tests, which isn't that useful yet."""
    def validate_p_test(s):
        name = 'test/problem_feeds/only_old_entries.rss'
        assert(validate_p(name, "A"))
    
    def validate_test(s):
        name = 'test/problem_feeds/no_feed_info.xml'
        v = get_validation_output(name, "A")
        s.assertNotEqual(v,True)
        s.assertTrue("""line 2, column 0: Missing feed element: title
line 2, column 0: Missing feed element: id
line 2, column 0: Missing feed element: updated""" in v)
