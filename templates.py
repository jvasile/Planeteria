import os, cgi

class Template(object):
   errors = 'ignore'
   def __init__(self, interpolate):
      self.interpolate = interpolate
   def escape(self, s):
      return cgi.escape(s)
   def write(self, output_dir, fname, errors=None):
      if not errors:
         errors = self.errors
      with open(os.path.join(output_dir, fname), "w") as FILE:
         FILE.write(self.render().encode('latin-1', errors))
   def render(self):
      return ''

class XML_Template(Template):
   errors = 'xmlcharrefreplace'

class OPML(XML_Template):
   def feeds(self):
      s = ''
      for f in self.interpolate['Feeds']:
         s += """    <outline type="rss" text="%s" title="%s" xmlUrl="%s" image="%s"/>\n""" % (f['author'], f['title'], self.escape(f['url']), self.escape(f['image']))
      return s

   def render(self):
      self.interpolate['rendered_feeds'] = self.feeds()
      return """<?xml version="1.0"?>
<opml version="1.1">
  <head>
    <title type="text/plain">%(title)s</title>
    <dateModified>%(datemodified)s</dateModified>
    <ownerName>%(user)s</ownerName>
    <ownerEmail>%(email)s</ownerEmail>
  </head>

  <body>
%(rendered_feeds)s  </body>
</opml>
""" % self.interpolate

class Atom(XML_Template):
   def render(self):
      o = self.interpolate
      for k in ['title', 'name']:
         o['e'+k] = self.escape(o[k])

      o['rendered_items'] = self.items()

      return """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:planet="%(feed_page)s" xmlns:indexing="urn:atom-extension:indexing" indexing:index="no"><access:restriction xmlns:access="http://www.bloglines.com/about/specs/fac-1.0" relationship="deny"/>
  <title type="text/plain">%(ename)s</title>
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
      items = self.interpolate['Items']
      s = ''
      for i in items:
         for k in ['title', 'subtitle']:
            i['e'+k] = cgi.escape(i[k])
         i['econtent'] = i['content'].decode('latin-1', 'ignore')
         s += """<entry>
      <id>%(id)s</id>
      <title type="text/plain">%(etitle)s</title>
      <summary>%(summary)s</summary>
      <updated>%(updated)s</updated>
      <link href="%(link)s" rel="alternate" type="text/html"/>""" % i
         if 'author' in i:
            s+="""
      <author><name>%(author)s</name></author>""" % i

         s += """ 
      <source>
	<id>%(feed_id)s</id>
""" % i

         for l in i['links']:
            l['ehref'] = cgi.escape(l['href'])
            s += '        <link href="%(ehref)s" rel="%(rel)s" type="%(type)s" />\n' % l

         s += """	<subtitle>%(esubtitle)s</subtitle>
	<title>%(feed_name)s</title>
	<updated>%(updated)s</updated>
      </source>

      <content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">%(econtent)s</div></content>
 </entry>
 """ % i
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

   def header(self):
      s = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   <base href="%(base_href)s" />
"""  % self.interpolate
      if 'owner_name' in self.interpolate:
         s += '     <meta name="author" content="%(owner_name)s" />\n'  % self.interpolate
      if 'admin' in self.interpolate:
         s += '     <meta name="description" content="Admin interface for a planet blog aggregator" />\n'

      s += """   <meta name="license" content="Various.  See source blogs for individual posts." />
   <meta name="generator" content="%(generator)s">
   <meta name="keywords" content="Planet, admin, metaplanet, hackervisions, blog, aggregator" />
   <meta name="robots" content="index, follow, noarchive" />
   <meta name="googlebot" content="noarchive" />
"""  % self.interpolate
      if 'Items' in self.interpolate:
         s += '   <link rel="alternate" type="application/rss+xml" href="atom.xml" title="All these posts as one feed" />\n'  % self.interpolate

      s += """   <title>%(title)s</title>
   <link rel="stylesheet" href="pub.d/form.css" type="text/css" />
   <link rel="stylesheet" href="pub.d/screen.css" type="text/css" />
   <link rel="stylesheet" href="pub.d/venus.css" type="text/css" />
"""  % self.interpolate

      if 'admin' in self.interpolate:
         s += """     <script src="pub.d/admin.js" type="text/javascript"></script>
     <script type="text/javascript">
        %(push_feeds)s
     </script>
"""  % self.interpolate
      s += """</head>
<body>

<div id="wrap">
   <div id="header">
"""  % self.interpolate

      if 'name' in self.interpolate:
         s += '         <h1 id="logo-text"><a href="%(base_href)s%(direc)s" accesskey="1" title="">%(name)s</a></h1>\n'  % self.interpolate
      else: 
         s += '         <h1 id="logo-text"><a href="" accesskey="1" title="">%(website_name)s</a></h1>\n'  % self.interpolate

      s += """      <p id="slogan">Blog aggregation.  By your community, for your community.</p>
      <a href="%(base_href)s"><div id="header-image"><img src="pub.d/images/planeteria_200.png" /></div></a>
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
      <p>You can have the <a href="copyright.html">code</a> to this page under the terms of the <a href="http://www.fsf.org/licensing/licenses/agpl-3.0.html">AGPLv3</a>.</p>
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
         for e in ['channel_link', 'channel_title_plain', 'channel_faceheight', 'channel_faceurl', 'channel_facewidth', 'link', 'author']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''

         o['rendered_channel_language'] = self.ensure('channel_language', ' lang="%(channel_language)s"', o)
         o['rendered_title_language'] = self.ensure('title_language', ' lang="%(title_language)s"', o)
         o['rendered_content_language'] = self.ensure('content_language', ' lang="%(content_language)s"', o)
         o['rendered_faceurl'] = self.ensure('channel_faceurl', '            <img class="face" src="%(escaped_channel_faceurl)s" width="%(escaped_channel_facewidth)s" height="%(escaped_channel_faceheight)s" alt="">\n', o)


         o['rendered_content'] = o['content'].decode('latin-1', 'ignore')

         for e in ['channel_link', 'channel_title_plain', 'link', 'author']:
            try:
               o['escaped_'+e] = self.escape(o[e])
            except KeyError:
               o['escaped_'+e] = ''

         o['rendered_author'] = self.ensure('escaped_author', '%(escaped_author)s | ', o)
         if 'new_date' in o:
            s += '   <div class="dateheader">%(new_date)s</div>\n'
         s += """   <div class = "entry">
      <div class="entrybody" id="%(id)s"%(rendered_channel_language)s>
         %(rendered_faceurl)s

         <div class="entrytitle" %(rendered_title_language)s>
            <a href="%(escaped_channel_link)s" title="%(escaped_channel_title_plain)s">%(channel_name)s</a>: 
            <a href="%(escaped_link)s">%(title)s</a>
         </div>

         <div class="content"%(rendered_content_language)s>
            %(rendered_content)s
          </div>
                        
         <p align="right">
            <a href="%(escaped_link)s">
            %(rendered_author)s%(escaped_channel_title_plain)s | 
            %(date)s</a></a>
         </p>
      </div>
   </div>
""" % o
      return s

   def render_feeds(self):
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

         s += '            <li><a href="%(escaped_url)s" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"></a> <a %(rendered_link)s%(rendered_message)s>%(author)s</a></li>\n' % o
      return s

   def render_channels(self):
      if not 'Channels' in self.interpolate:
         return ''
      assert False, "I don't think we use Channels, but if you see this, I'm wrong so finish this function."
      s=''
      for o in self.interpolate['Channels']:
         s += """            <li>
               <a href="<TMPL_VAR url ESCAPE="HTML">" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"></a> <a <TMPL_IF link>href="<TMPL_VAR link ESCAPE="HTML">" </TMPL_IF><TMPL_IF message>class="message" title="<TMPL_VAR message ESCAPE="HTML">"</TMPL_IF><TMPL_UNLESS message>title="<TMPL_VAR title_plain ESCAPE="HTML">"</TMPL_UNLESS>><TMPL_VAR name></a>
            </li>
"""
      return s

   def render(self):
      o = self.interpolate
      o['rendered_sidebar'] = self.ensure('sidebar')
      o['rendered_items'] = self.items()
      o['rendered_feeds'] = self.render_feeds()
      o['rendered_channels'] =  self.render_channels()
      s="""<div id="left">

<!-- BEGIN FEEDS -->
%(rendered_items)s

</div>	<!-- end left -->

<div id="right">
   <div class="entry">
      <div class="entrytitle">Subscriptions</div>
      <ul>
%(rendered_feeds)s
%(rendered_channels)s
            <li> <a href="%(feed_url)s" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"> All feeds in one</a></li>
            <li> <a href="%(opml_url)s" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"> All feeds as OPML</a></li>
      </ul>
   </div>

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
	  <li><a href="admin.py">Admin interface</a></li>
	</ul>
   </div>
</div>	
""" % o
      return self.header() + s + self.footer()

class Copyright(HTML_Template):
   def render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Copyrights</div>

    <p>Individual posts are copyright by their authors and I claim no
    exclusive rights to them.  Click through the posts to the parent
    blogs and you should be able to find terms for reproduction.</p>

    <p>All of the software behind this site is open source and some of
    it was written by others.  In particular, Planeteria software is
    based on <a href="http://intertwingly.net/code/venus/">Venus</a>,
    which is GPL-licensed.</p>

    <p>Everything else (i.e. the stuff I produced) is available under
    the <a
    href="http://www.fsf.org/licensing/licenses/agpl-3.0.html">AGPLv3</a>.</p>

    <p>I will at some point package the source code, templates, and
    supporting scripts.  </b>Right now the code has some trashy hacks
    and the setup is extremely ugly.</b> But now that I have running
    code, I'll clean it up slowly.  And then the code will be
    available from this page.  But until I get around to it, there's
    always bazaar:

    <blockquote>
    bzr get http://bzr.hackervisions.org/planeteria
    </blockquote></p> 

    <p>Run the setup script in the root of that branch. See the <a
    href="/readme.html">readme</a> for details.</p>

    <p>The setup script will download my mildly adjusted version of
    Venus, which resides in a separate branch at
    http://bzr.hackervisions.org/venus</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class Contact(HTML_Template):
   def render(self):
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
   def render(self):
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

class Tos(HTML_Template):
   def render(self):
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

    <p>From time to time, I might add new terms here.  You agree to
    watch this page for changes and be bound by those new terms.</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()

class Index(HTML_Template):
   def render(self):
      return self.header() + """
<div id="left">

<!-- BEGIN FEEDS -->
<TMPL_LOOP Items>
   <TMPL_IF new_date><div class="dateheader"><TMPL_VAR new_date></div></TMPL_IF>

   <div class = "entry">
      <div class="entrybody" id="<TMPL_VAR id>"<TMPL_IF channel_language> lang="<TMPL_VAR channel_language>"</TMPL_IF>>
         <TMPL_IF channel_faceurl>
            <img class="face" src="<TMPL_VAR channel_faceurl ESCAPE="HTML">" width="<TMPL_VAR channel_facewidth ESCAPE="HTML">" height="<TMPL_VAR channel_faceheight ESCAPE="HTML">" alt="">
         </TMPL_IF>

         <div class="entrytitle" <TMPL_IF title_language> lang="<TMPL_VAR title_language>"</TMPL_IF>>
            <a href="<TMPL_VAR channel_link ESCAPE="HTML">" title="<TMPL_VAR channel_title_plain ESCAPE="HTML">"><TMPL_VAR channel_name></a>: 
            <a href="<TMPL_VAR link ESCAPE="HTML">"><TMPL_VAR title></a>
         </div>

         <div class="content"<TMPL_IF content_language> lang="<TMPL_VAR content_language>"</TMPL_IF>>
            <TMPL_VAR content>
         </div>
                        
         <p align="right">
            <a href="<TMPL_VAR link ESCAPE="HTML">">
            <TMPL_IF author><TMPL_VAR author ESCAPE="HTML"> | </TMPL_IF>
            <TMPL_VAR channel_title_plain ESCAPE="HTML"> | 
            <TMPL_VAR date></a></a>
         </p>
      </div>
   </div>
</TMPL_LOOP>
</div>	<!-- end left -->

<div id="right">

   <div class="entry">
      <div class="entrytitle">Subscriptions</div>
      <ul>
         <TMPL_LOOP Feeds>
            <li>
               <a href="<TMPL_VAR url ESCAPE="HTML">" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"></a> <a <TMPL_IF link>href="<TMPL_VAR link ESCAPE="HTML">" </TMPL_IF><TMPL_IF message>class="message" title="<TMPL_VAR message ESCAPE="HTML">"</TMPL_IF><TMPL_UNLESS message>title="<TMPL_VAR title_plain ESCAPE="HTML">"</TMPL_UNLESS>><TMPL_VAR author></a>
            </li>
         </TMPL_LOOP>

         <TMPL_LOOP Channels>
            <li>
               <a href="<TMPL_VAR url ESCAPE="HTML">" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"></a> <a <TMPL_IF link>href="<TMPL_VAR link ESCAPE="HTML">" </TMPL_IF><TMPL_IF message>class="message" title="<TMPL_VAR message ESCAPE="HTML">"</TMPL_IF><TMPL_UNLESS message>title="<TMPL_VAR title_plain ESCAPE="HTML">"</TMPL_UNLESS>><TMPL_VAR name></a>
            </li>
         </TMPL_LOOP>
            <li> <a href="<TMPL_VAR feed_url>" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"> All feeds in one</a></li>
            <li> <a href="<TMPL_VAR opml_url>" title="subscribe"><img src="pub.d/images/feed-icon-10x10.png" alt="(feed)"> All feeds as OPML</a></li>
      </ul>
   </div>


   <TMPL_VAR sidebar>

   <div class="entry">
      <div class="entrytitle">Copying</div>
      <p>Posts are copyright their respective authors. Click through to
      see each site's terms for redistribution.</p>
   </div>

   <div class="entry">
      <div class="entrytitle">Meta</div>
        <ul>
	  <li><TMPL_VAR date></li>
	  <li><a href="admin.py">Admin interface</a></li>
	</ul>
   </div>
</div>	
""" % self.interpolate + self.footer()


class Welcome(HTML_Template):
   def render(self):
      return self.header() + """
<div id="left">

  <div class = "entry">
    <div class="entrytitle">Your New Planet</div>

    <p>Your planet has been created, but you need to set it up via <a
    href="<TMPL_VAR base_href><TMPL_VAR direc>/admin.py">the admin interface</a> before it is
    functional.</p>

  </div> <!-- end entry -->

</div> <!-- end left -->

<div id="right">
  %s
</div>	<!-- end right -->
""" % self.sidebar() + self.footer()