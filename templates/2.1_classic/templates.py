import os, cgi, codecs, re
from BeautifulSoup import BeautifulSoup

class Template(object):
   errors = 'ignore'
   def __init__(self, interpolate):
      self.interpolate = interpolate # interplation dict
   def escape(self, s):
      if s:
         return cgi.escape(s)
      else:
         return s
   def write(self, output_dir, fname, errors=None):
      if not errors:
         errors = self.errors
      r = self._render()
      with codecs.open(os.path.join(output_dir, fname), "w", "utf-8") as FILE:
         FILE.write(r)
   def _render(self):
      return ''
   def render(self):
      a = self._render()
      if isinstance(a, unicode):
         a = a.encode('utf-8')
      return a


class XML_Template(Template):
   errors = 'xmlcharrefreplace'

class OPML(XML_Template):
   def feeds(self):
      s = ''
      for f in self.interpolate['Feeds']:
         g = {}
         for field in ['title', 'author', 'url', 'image']:
            g['e'+field] = self.escape(f[field])
         s += """    <outline type="rss" text="%(eauthor)s" title="%(etitle)s" xmlUrl="%(eurl)s" imageUrl="%(eimage)s"/>\n""" % g
      return s

   def _render(self):
      self.interpolate['rendered_feeds'] = self.feeds()
      return """<?xml version="1.0"?>
<opml version="1.1">
  <head>
    <title>%(title)s</title>
    <dateModified>%(datemodified)s</dateModified>
    <ownerName>%(user)s</ownerName>
    <ownerEmail>%(email)s</ownerEmail>
  </head>

  <body>
%(rendered_feeds)s  </body>
</opml>
""" % self.interpolate

class Atom(XML_Template):
   def _render(self):
      o = self.interpolate
      for k in ['title', 'name']:
         o['e'+k] = self.escape(o[k])

      o['rendered_items'] = self.items()

      return """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:indexing="urn:atom-extension:indexing" indexing:index="no"><access:restriction xmlns:access="http://www.bloglines.com/about/specs/fac-1.0" relationship="deny"/>
  <title type="text">%(ename)s</title>
  <updated>%(updated)s</updated>
  <generator uri="%(generator_uri)s">%(generator)s</generator>
  <author>
    <name>%(user)s</name>
    <email>%(email)s</email>
  </author>
  <id>%(feed_url)s</id>
  <link href="%(feed_url)s" rel="self" type="application/atom+xml"/>
  <link href="%(feed_page)s" rel="alternate"/>
     %(rendered_items)s
</feed>
""" % o
   def items(self):
      items = self.interpolate['ItemsXML']
      s = ''
      for i in items:
         for k in ['title', 'subtitle']:
            i['e'+k] = cgi.escape(i[k])
         s += u'<entry>\n      <id>%(id)s</id>\n' % i
         s += u'      <title type="text">%(etitle)s</title>\n' % i
         s += u'\n      <summary type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">' + i['summary_encoded'] + u'\n     </div>\n     </summary>\n' % i
         s += u'      <updated>%(updated)s</updated>\n' % i
         s += u'      <link href="%(link)s" rel="alternate" type="text/html"/>\n' % i
         if 'author' in i:
            s+=u'\n      <author><name>%(author)s</name></author>\n' % i
         s += u'\n      <source>\n      <id>%(feed_id)s</id>\n' % i

         for l in i['links']:
            if 'href' in l:
               l['ehref'] = cgi.escape(l['href'])
               s += u'        <link href="%(ehref)s" rel="%(rel)s" type="%(type)s" />\n' % l

         s += u"""	<subtitle>%(esubtitle)s</subtitle>
	<title>%(feed_name)s</title>
	<updated>%(updated)s</updated>
      </source>""" % i
         s += u'\n      <content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">' + i['content_encoded'] + u'\n     </div>\n     </content>\n' % i
         s +=' </entry>\n'
      return s

class HTML_Template(Template):
   def sidebar(self):
      return """  <div class="entry">
    <div class="entrytitle">About</div> 
    <p>Planet websites are community blog aggregators. Use
      Planeteria to collect all the personal blogs in your
      community or team and really get to know the people
      behind a project.</p>

    <p>Planeteria is not a feed reader, it's a feed
      sharer. After you make your planet, tell people about
      it. That's the whole point of community-building!</p>
  </div>
"""
   def render_contact_box(self):
      i = self.interpolate
      owner = email = None
      if 'owner_name' in i:
         owner = '%(owner_name)s'  % i
      if 'owner_email' in i:
         email = '%(owner_email)s'  % i
         email = email.replace('@', " AT ").replace('.', " DOT ")
      if not owner and not email:
         return ''

      s = '<div class = "entry">\n   <div class="entrytitle">Contact</div>\n<p>Want to see your blog on this planet?  '

      if owner:
         s += "It's maintained by %s" % owner
         if email:
            s += " (%s).  Get in touch and let them know you want to join!" % email
         else:
            s += ".  If you know how to reach this person, let them know you want to join the planet!"
      else:
         if email:
            s += "Contact the planet's maintainer at %s and let them know you want to join!" % email
         else:
            s += "If you know how to reach the maintainer of this planet, get in touch and let them know you want to join!"
         
      s += "</p>\n</div>"
      return s

   def render_donations(self):
      return """
  <div class = "entry">
    <div class="entrytitle">Donations</div>
    <p>If you find Planeteria.org or the free software on which it runs useful, please help support this site.</p>
    <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
       <input type="hidden" name="cmd" value="_s-xclick">
       <input type="hidden" name="hosted_button_id" value="49HBMGVGUAHPU">
       <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
       <img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
    </form>
    <p><b>Bitcoin:</b> 17XkPWnefx3gYHFax74hNRfj6NtrGyJ4VN</p>
  </div> <!-- end entry -->"""

   def header(self):
      i = self.interpolate
      s = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   <base href="%(base_href)s" />
"""  % i
      if 'owner_name' in self.interpolate:
         s += '     <meta name="author" content="%(owner_name)s" />\n'  % i
      if 'admin' in self.interpolate:
         s += '     <meta name="description" content="Admin interface for a planet blog aggregator" />\n'

      s += """   <meta name="license" content="Various.  See source blogs for individual posts." />
   <meta name="generator" content="%(generator)s" />
   <meta name="keywords" content="Planet, admin, metaplanet, hackervisions, blog, aggregator" />
   <meta name="robots" content="index, follow, noarchive" />
   <meta name="googlebot" content="noarchive" />
   <title>%(title)s</title>
   <link rel="stylesheet" href="pub.d/form.css" type="text/css" />
   <link rel="stylesheet" href="pub.d/screen.css" type="text/css" />
   <link rel="stylesheet" href="pub.d/venus.css" type="text/css" />
""" % i

      if 'feed_url' in self.interpolate:
         s += '   <link rel="alternate" type="application/rss+xml" href="%(feed_url)s" title="All these posts as one feed" />\n'  % i
      if 'admin' in i:
         s += '     <script src="pub.d/admin.js" type="text/javascript"></script>\n     <script type="text/javascript">\n        %(push_feeds)s\n     </script>\n' % i
      s += '</head>\n<body>\n<div id="wrap">\n   <div id="header">\n'  % i

      if i['base_href'].startswith('file://'):
         i['index'] = 'index.html'
      else:
         i['index'] = ''

      if 'name' in i:
         s += '         <h1 id="logo-text"><a href="%(base_href)s%(direc)s/%(index)s" accesskey="1" title="%(name)s">%(name)s</a></h1>\n'  % i
      else: 
         s += '         <h1 id="logo-text"><a href="%(index)s" accesskey="1" title="site:%(website_name)s">%(website_name)s</a></h1>\n'  % i

      s += """      <p id="slogan">Blog aggregation.  By your community, for your community.</p>
      <a href="%(base_href)s%(index)s"><div id="header-image"><img src="pub.d/images/planeteria_200.png" /></div></a>
   </div>

   <!-- content -->
   <div id="content-outer" class="clear"><div id="content-wrap">
      <div id="content">
""" % self.interpolate

      return s

   def footer(self):
      return """
      </div>  <!-- end content -->
   </div> <!-- end content-outer -->

   <div id="footer-wrap">
      <div id="footer-outer">
         <div id="footer-bottom">
      <p><a href="thanks.html">Thanks</a> | <a href="contact.html">Contact</a> | <a href="copyright.html">Copyright</a> | <a href="tos.html">Terms of Use</a></p>
      <p>You can have the <a href="https://github.com/jvasile/Planeteria">code</a> to this page under the terms of the <a href="http://www.fsf.org/licensing/licenses/agpl-3.0.html">AGPLv3</a>.</p>
   </div></div></div>

</div> <!-- end wrap -->

</body>
</html>
"""

class Planet_Page(HTML_Template):
   def ensure(self, key, format_str=None, dictionary=None, default=''):
      if not dictionary:
         dictionary = self.interpolate

      newline=''
      if not format_str:
         format_str =  "%(" + key + ")s"
      elif format_str.endswith("\n"):
         format_str = format_str[:-1]
         newline="\n"

      try:
         if dictionary[key] != None and dictionary[key] != '':
            return eval ("'%s'" % format_str + " % dictionary") + newline
         return newline
      except KeyError:
         return default

   def items(self):
      s = ''
      for o in self.interpolate['Items']:
         for e in ['channel_link', 'channel_title_plain', 'channel_faceheight', 'channel_image', 'channel_facewidth', 'link', 'author', 'title']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''

         o['rendered_channel_language'] = self.ensure('channel_language', ' lang="%(channel_language)s"', o)
         o['rendered_title_language'] = self.ensure('title_language', ' lang="%(title_language)s"', o)
         o['rendered_content_language'] = self.ensure('content_language', ' lang="%(content_language)s"', o)
         o['rendered_image'] = self.ensure('channel_image', '            <img class="face" src="%(escaped_channel_image)s" width="%(escaped_channel_facewidth)s" height="%(escaped_channel_faceheight)s" alt="">\n', o)

         for e in ['channel_link', 'channel_title_plain', 'link', 'author']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''
               
         #o['rendered_author'] = self.ensure('escaped_author', '%(escaped_author)s', o)
         if 'new_date' in o:
            s += '   <div class="dateheader">%(new_date)s</div>\n'

         s += """   <div class = "entry">
      <div class="entrybody" id="%(id)s"%(rendered_channel_language)s>

         <div class="entrytitle" %(rendered_title_language)s>
            <div class="entrytitleauthor"><a href="%(escaped_channel_link)s" title="%(escaped_channel_title_plain)s">%(name)s </a></div><br />
         %(rendered_image)s
            <a href="%(escaped_link)s">%(title)s</a> 
        </div>

         <div class="content"%(rendered_content_language)s>
            %(content_encoded)s
          </div>
                        
         <p align="right">
            <a href="%(escaped_link)s">
            %(name)s | %(escaped_channel_title_plain)s | 
            %(date)s</a></a>
         </p>
      </div>
   </div>
""" % o
      return s

   def render_feeds(self):
      """This is the list of feeds on the right of the page."""
      s=''
      for o in self.interpolate['Feeds']:
         for e in ['url', 'link', 'message', 'title_plain']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''
         o['rendered_link'] = self.ensure('escaped_link', 'href="%(escaped_link)s"', o)
         o['rendered_message'] = self.ensure('escaped_message', ' class="message" title="%(escaped_message)s"', 
                                             o, 
                                             default='title="%(escaped_title_plain)s"' % o)
         #if e['bozo']:
         #   o['rendered_bozo'] = '[B]'
         s += '            <li><a href="%(escaped_url)s" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"></a> <a %(rendered_link)s%(rendered_message)s>%(author)s</a></li>\n' % o
      return s

   def _render(self):
      o = self.interpolate
      o['rendered_sidebar'] = self.ensure('sidebar')
      o['rendered_items'] = self.items()
      o['rendered_feeds'] = self.render_feeds()
      o['rendered_donations'] = self.render_donations()
      o['rendered_contact'] = self.render_contact_box()
      s="""<div id="left">

<!-- BEGIN FEEDS -->
%(rendered_items)s

</div>	<!-- end left -->

<div id="right">
   <div class="entry">
      <div class="entrytitle">Subscriptions</div>
      <ul>
%(rendered_feeds)s
            <li> <a href="%(feed_url)s" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"> All feeds in one</a></li>
            <li> <a href="%(opml_url)s" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"> All feeds as OPML</a></li>
      </ul>
   </div>

   %(rendered_contact)s
   %(rendered_donations)s
   %(rendered_sidebar)s

   <div class="entry">
      <div class="entrytitle">Copying</div>
      <p>Posts are copyright their respective authors. Click through to
      see each site's terms for redistribution.</p>
   </div>

   <div class="entry">
      <div class="entrytitle">Meta</div>
        <ul>
	  <li>%(date)s</li>
	  <li><a href="/%(direc)s/admin.py">Admin interface</a></li>
	</ul>
   </div>
</div>	
""" % o
      return self.header() + s + self.footer()

class Snippet(HTML_Template):
   def ensure(self, key, format_str=None, dictionary=None, default=''):
      if not dictionary:
         dictionary = self.interpolate

      newline=''
      if not format_str:
         format_str =  "%(" + key + ")s"
      elif format_str.endswith("\n"):
         format_str = format_str[:-1]
         newline="\n"

      try:
         if dictionary[key] != None and dictionary[key] != '':
            return eval ("'%s'" % format_str + " % dictionary") + newline
         return newline
      except KeyError:
         return default

   def items(self):
      s = ''
      for o in self.interpolate['Items']:
         for e in ['channel_link', 'channel_title_plain', 'channel_faceheight', 'channel_image', 'channel_facewidth', 'link', 'author', 'title']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''

         o['rendered_channel_language'] = self.ensure('channel_language', ' lang="%(channel_language)s"', o)
         o['rendered_title_language'] = self.ensure('title_language', ' lang="%(title_language)s"', o)
         o['rendered_content_language'] = self.ensure('content_language', ' lang="%(content_language)s"', o)
         o['rendered_image'] = self.ensure('channel_image', '            <img class="face" src="%(escaped_channel_image)s" width="%(escaped_channel_facewidth)s" height="%(escaped_channel_faceheight)s" alt="">\n', o)

         for e in ['channel_link', 'channel_title_plain', 'link', 'author']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''
         if o['escaped_channel_title_plain'].startswith("Twitter /"):
            c = '<p>'+o['content_encoded'].split( o['escaped_channel_title_plain'].split(' / ')[1] )[1][2:]
            c = re.sub("(https?://[^ <]*)", r'<a href="\1">\1</a>', c)
            c = re.sub(r"\s#(\w+)", r'<a href="https://identi.ca/tag/\1">#\1</a>', c)
            c = re.sub(r"^#(\w+)", r'<a href="https://identi.ca/tag/\1">#\1</a>', c)
            s += c
         elif o['name'] == "Diaspora":
            c = o['content_encoded']
            c = re.sub("(https?://[^ <]*)", r'<a href="\1">\1</a>', c)
            s += c+'\n'
         elif o['name'] == "Github":
            soup = BeautifulSoup(o['content_encoded'])
            bq = soup.find('blockquote')
            if bq:
               c = bq.string
            else:
               bq = soup.find("div", { "class" : "message" })
               if bq:
                  if bq.string:
                     c = bq.string
                  else:
                     c = bq
               else:
                  c=""

            s += '<p><a href="%s">%s</a>: %s</p>' % (o['escaped_link'], o['escaped_title'].split(' ',1)[1], c)
         elif o['name'] == "Blog":
            soup = BeautifulSoup(o['content_encoded'])
            p = soup.findAll('p')
            if p:
               s += p[0].__repr__().replace('<br />', '').replace('<br>', '')
               
            else:
               s += o['content_encoded']
            if s.endswith('</p>'):
               s=s[:-4]
               s += ' (<a href="%s">blog</a>)</p>' % (o['escaped_link']) + '\n'
            else:
               s += ' (<a href="%s">blog</a>)' % (o['escaped_link']) + '\n'
         else:
            #print "|%s|" % o['name']
            s += o['content_encoded']+'\n'
      return s

   def _render(self):
      o = self.interpolate
      o['rendered_items'] = self.items()
      s="""%(rendered_items)s</div>""" % o
      return s
      #return self.header() + s + self.footer()

class Copyright(HTML_Template):
   def __init__(self, interpolate):
      HTML_Template.__init__(self, interpolate)
      self.interpolate['title'] = 'Code and Copyright'
   def _render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Copyrights</div>

    <p>Individual posts are copyright by their authors and I claim no
    exclusive rights to them.  Click through the posts to the parent
    blogs and you should be able to find terms for reproduction.</p>

    <p>All of the software behind this site is open source. Everything
    I produced is available under the <a
    href="http://www.fsf.org/licensing/licenses/agpl-3.0.html">AGPLv3
    license</a>.</p>

    <p>I will at some point package the source code.  <b>Right now the
    code has some trashy hacks and the setup is extremely ugly.</b>
    But now that I have running code, I'll clean it up slowly.  Please
    <a href="https://github.com/jvasile/Planeteria/issues">let me know
    about bugs</a>.  Soon the code will be available from this page.
    But until I get around to it, there's always GitHub:

    <blockquote>
    git clone git://github.com/jvasile/Planeteria.git
    </blockquote></p> 

    <p>Run generate.py in the root of that branch. See the <a
    href="https://github.com/jvasile/Planeteria/blob/master/README">readme</a>
    for details.</p>

    <p>A previous version of Planeteria was based on <a
    href="http://intertwingly.net/code/venus/">Venus</a>, which I
    highly recommend if you are trying to run just one planet.</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class Contact(HTML_Template):
   def _render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Contact Planeteria</div>

    <p>The best way to reach James Vasile is via email: james at
    hackervisions dot org.</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class Thanks(HTML_Template):
   def __init__(self, interpolate):
      HTML_Template.__init__(self, interpolate)
      self.interpolate['title'] = 'Thanks'

   def _render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Thanks!</div>

    <p>A project like this rests on a deep stack of impressive work
    freely shared by a multitude of others.  This page is where we
    thank those people and encourage you to check out their other
    work.</p>

    <ul>
    <li>I photoshopped the Planeteria logo 
    in <a href="http://www.gimp.org/">GIMP</a>
    from <a href="http://www.flickr.com/photos/wwworks/2222523486/">a
    public domain photo</a> found on Flickr.</li>

    <li>The <a href="/pub.d/images/silhouette2.png">Unknown Blogger
    avatar</a> is based on a photo I
    gimped off of Flickr.  Unfortunately, <a
    href="http://www.flickr.com/photos/n-o-n-o/3502226571">the link</a> went dead and I
    can no longer find it.  All of <a
    href="http://www.flickr.com/photos/n-o-n-o/">Nono Fara's
    photos</a> are beautiful, though, so poke through her stream for
    some nice shots.</li>

    <li>I originally based this software on <a
    href="http://www.planetplanet.org/">Planet Planet</a>, but quickly
    moved to build instead on <a
    href="http://intertwingly.net/code/venus/">Venus</a>.  Later I
    discarded those dependencies for more flexibility, but my code is
    less robust as a result.  Venus is good stuff and if you're only
    running one planet, I highly recommend it.</li>

    <li>The bulk of the CSS on this site is from a template called
    FreshPick by <a href="http://www.styleshout.com/">Erwin
    Aligam</a>.  Some form-specific CSS came from <a
    href="http://www.alistapart.com/articles/prettyaccessibleforms/">A
    List Apart</a>.  I also grabbed some from <a
    href="http://meyerweb.com/eric/thoughts/2007/05/01/reset-
    reloaded/">Eric Meyer</a>.</li>

    <li>I scavenged some Javascript from the web: <a
    href="http://www.webmasterworld.com/forum91/441.htm">hidediv</a>.</li>

    <li>I grabbed this <a
    href="http://code.activestate.com/recipes/82465/">mkdir</a>
    routine.</li>

    </ul>
  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class TOS(HTML_Template):
   def __init__(self, interpolate):
      HTML_Template.__init__(self, interpolate)
      self.interpolate['title'] = 'Terms of Service'

   def _render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Terms of Use</div>

    <p>By accessing this site, you agree to the following terms:</p>

    <p>You grant me (James Vasile) a worldwide, perpetual,
    sublicensable royalty-free license to reprint any content you
    contribute to this site, in verbatim or modified form, and in any
    medium.  This doesn't include stuff we pull in via rss and
    atom.</p>

    <p>This website inevitably collects some data about users, both in
    server logs and in the content you contribute. I won't share your
    data with spammers.</p>

    <p>You agree not to rely on this site for anything crucial.  It
    might disappear or break without notice and I'm making no
    commitment to maintain it or fix it quickly (or ever).  If you
    want reliability, talk to me and we'll come up with something that
    works.</p>

    <p>I store your password as plain, unobfuscated text in my
    database.  Please do not use a real password on this site.
    Security ranges from lax to nonexistent.  It's just feeds, and
    it's not worth the effort of real security.</p>

   <p>If your planet is inactive (i.e. nobody is
    pulling the feed or viewing the planet page on a regular basis),
    I'm probably going to delete it to conserve resources.</p>

    <p>The email address you enter is viewable by anybody who comes to
    your admin page or pulls your feed.  Feel free to lie about your
    address.</p>

    <p>From time to time, I might add new terms here.  You agree to
    watch this page for changes and be bound by those new terms.</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class Main_Page(HTML_Template):
   def __init__(self, interpolate):
      HTML_Template.__init__(self, interpolate)
      self.interpolate['title'] = 'Welcome to Planeteria'

   def _render(self):
      o = self.interpolate
      for field in ['error', 'direc', 'subdirectory', 'turing']:
         if not field in self.interpolate:
            self.interpolate[field] = ''
      o['rendered_donations'] = self.render_donations()
      if o['base_href'] == '/':
         o['domain'] = "Your planet URL will be on this website in the subdirectory you specify,"
      else:
         o['domain'] = "Your planet URL will be %(base_href)ssubdirectory," % o

      return self.header() + """

<div id="left">

  <div id="error">%(error)s</div>

  <div class = "entry">
    <div class="entrytitle">Get Your Own Planet</div>
    <p>You can have a planet of your very own!  Pull together all the
      blogs around your project or community.  Just fill out this form:</p>

    <form method="post" action="new_planet.py" class="cmxform"> 

      <label for="subdirectory">Subdirectory:</label>
      <input type="text" size=40 id="subdirectory" name="subdirectory" value="%(subdirectory)s" /><br />
      %(domain)s
      and the subdirectory may only consist of letters and numbers.<br/>

      <br /><br />

      <label for="turing">Turing Test:</label>
      <input type="test" size="40" name="turing" value="%(turing)s"/><br />
      Please prove you are human by answering this question: Do you love?<br />

      <div align="center"><input type="submit" name="submit" value="Create Planet" /></div>

    </form>

  </div> <!-- end entry -->

  <div class = "entry">
    <div class="entrytitle">Planets for Everybody!</div>
    <p>A planet is a collection of posts from many different blogs,
      all somewhat related to one topic.  It's a great way to keep
      tabs on a subject, a community, a technology, a team, a project
      or anything else that attracts a diverse range of bloggers.</p>

    <p><b>Community.</b> Planets are a great way to focus and foster
      community.  It's easy to get everybody in the community talking
      with each other when you're all reading each other's blogs!</p>

    <p><b>Curation.</b> One stop curation allows a planet to become
      the definitive collection of news about a topic.  Each planet is
      a feed that can be imported into an RSS reader.  Planets allow
      you to pull together the best blogs about a topic so others
      don't have to do the leg work.  And you can get your entire
      audience reading the newest blogs simply by updating the
      planet.</p>

    <p><b>Early News.</b> Many planets collect the personal blogs of
      the people who work on a project.  Often the interesting
      developments that will eventually become front-page news on a
      project start as small personal milestones.  If you want to know
      where a project is going, watch its planet.  That's where all
      the early action is.</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  <div class = "entry">
    <div class="entrytitle">Some Awesome Planets</div>
    <ul>
      <li><a href="freedombox">FreedomBox</a></li>
      <li><a href="planetnyc">Freedom To Share in NYC</a></li>
      <li><a href="wfs">Women in Free Software</a></li>
    </ul>
  </div> <!-- end entry -->

   %(rendered_donations)s
</div>	<!-- end right -->
""" % self.interpolate + self.footer()

class Welcome(HTML_Template):
   def _render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Your New Planet</div>
    <p>Your planet has been created, but you need to set it up via <a
    href="%(base_href)s%(direc)s/admin.py">the admin interface</a> before it is
    functional.</p>
  </div> <!-- end entry -->""" % self.interpolate  + """
</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class Admin(HTML_Template):
   def render_feeds(self):
      s = ''
      for o in self.interpolate['Feeds']:
         if 'image' in o and o['image']:
            o['rendered_image'] = '<img class="face" src="%(image)s" width="%(facewidth)s" height="%(faceheight)s" alt="" />\n' % o
         else:
            o['rendered_image'] = '<img class="face" src="/pub.d/images/silhouette2.png" />\n'
         s += """
		<tr class="%(row_class)s" id="feed_row%(idx)s">
                  <td style="vertical-align:middle" class="entrytitleauthor">
                      %(rendered_image)s
                  </td>
		  <td style="text-align:left">
		    <input type="hidden" name="section%(idx)s" id="section%(idx)s" value="%(section)s" />
		    <input type="hidden" name="delete%(idx)s" id="delete%(idx)s" value="0" />
		    <a href="javascript:rm_feed(%(idx)s)"><img class="feedbtn" src="/pub.d/images/rm-feed.png"></a> <label for="name%(idx)s">Feed Name:</label><br />
		       <input type="text" size=40 name="name%(idx)s" id="name%(idx)s" value="%(name)s"><br />
		       <label for="feedurl%(idx)s">Feed URL:</label><br />
		       <input type="text" size=40 name="feedurl%(idx)s" id="feedurl%(idx)s" value="%(feedurl)s"><br />
		       <label for="image%(idx)s">Image URL:</label><br />
		       <input type="text" size=40 name="image%(idx)s" id="image%(idx)s" value="%(image)s"><br />		    
                  </td></tr>
""" % o
      return s
   def _render(self):
      o = self.interpolate
      o['sidebar'] = self.sidebar()
      o['rendered_feeds'] = self.render_feeds()
      if o['password'] == 'passme':
         o['passme'] = "If you don't know the password, try the default password: passme.  You are encouraged to change this password."
      else:
         o['passme']=''

      return self.header() + """
<div id="left">

  <div id="error">%(error)s</div>

  <form method="post" class="cmxform">
    <input type=hidden name="Timestamp" value="%(timestamp)s" />
    <div> <!-- need this div b/c form needs to be enclosed in a block element per http://objectmix.com/javascript/23328-dynamic-form-fields-added-appendchild-innerhtml-do-not-post-submit-firefox.html -->

      <div class = "entry">
        <div class="entrytitle">Planet Config</div>
        <ol>
          <li>%(planet_name_input)s</li>
          <li>%(owner_name_input)s</li>
          <li>%(owner_email_input)s</li>
    
    Your email address is viewable by anybody who comes to this page
    or pulls your feed.  Feel free to lie about it.<br />

        </ol>
      </div> <!-- end entry -->

      <div class = "entry" id="FeedsBody">
        <div class="entrytitle">Feeds <a href="javascript:add_feed()"><img src="pub.d/images/add-feed.png" width="14" height="14" border="0" alt="Add new feed button" name="AddFeedBtn" class="feedbtn"></a></div>
	<p>Use the <a href="javascript:add_feed()"><img src="pub.d/images/add-feed.png" width="14" height="14" border="0" alt="Add new feed button" name="AddFeedBtn" class="feedbtn"></a> and <img src="pub.d/images/rm-feed.png" width="14" height="14" border="0" alt="Remove feed sample" class="feedbtn"> buttons to add and remove feeds.</p>
        <div id="feeds">
	  <table id="feed_table"><tbody id="feeds_tbody">
          %(rendered_feeds)s
          </tbody></table>
        </div><!-- end feeds -->
      </div> <!-- end entry -->

      <div class = "entry" id="ChangeAuth">
        <div class="entrytitle">Change Password</div>
	%(change_pass_input)s<br />
        If you want to change your password, enter a new one here. I
        store your password as plain, unobfuscated text in my
        database.

      </div> <!-- end entry -->

      <div class = "entry" id="AuthGo">
        <div class="entrytitle">Save Changes</div>
	%(pass_input)s
        <input type="submit" value="Save Changes"><br />
	%(passme)s
      </div> <!-- end entry -->

      <div class="entry">
        <div class="entrytitle">Patience Please</div>
         After you save your changes, it will take a bit of time for
         your page and feed to update, so don't freak out if you don't
         see your changes immediately.
      </div>

   </div></form>
</div>	<!-- end left -->
<div id="right">
  %(sidebar)s
</div>	<!-- end right -->
""" % o + self.footer()

