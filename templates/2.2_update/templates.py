import os, cgi, codecs, re
from jinja2 import Environment, FileSystemLoader
from BeautifulSoup import BeautifulSoup
import util as u

Template_Dir = os.path.dirname(u.get_source_path())
JinjaEnv = Environment(loader=FileSystemLoader(Template_Dir))

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

class HTML_Jinja_Template(Template):
   def __init__(self, interpolate, template_fname):
      Template.__init__(self, interpolate)
      self.template_fname = template_fname
   def _render(self):
      template = JinjaEnv.get_template(self.template_fname)
      return template.render(**self.interpolate)


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
   <link rel="stylesheet" href="/pub.d/css/form.css" type="text/css" />
   <link rel="stylesheet" href="/pub.d/css/screen.css" type="text/css" />
   <link rel="stylesheet" href="/pub.d/css/venus.css" type="text/css" />
""" % i

      if 'feed_url' in self.interpolate:
         s += '   <link rel="alternate" type="application/rss+xml" href="%(feed_url)s" title="All these posts as one feed" />\n'  % i
      if 'admin' in i:
         s += '     <script src="/pub.d/admin.js" type="text/javascript"></script>\n     <script type="text/javascript">\n        %(push_feeds)s\n     </script>\n' % i
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
      <a href="%(base_href)s%(index)s"><div id="header-image"><img src="/pub.d/img/planeteria_200.png" /></div></a>
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
      <p><a href="about.html#thanks">Thanks</a> | <a href="about.html#contact">Contact</a> | <a href="about.html#copying">Copying</a> | <a href="about.html#tos">Terms of Use</a></p>
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
         s += '            <li><a href="%(escaped_url)s" title="subscribe"><img src="/pub.d/img/feed-icon-10x10.png" alt="(feed)"></a> <a %(rendered_link)s%(rendered_message)s>%(author)s</a></li>\n' % o
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
            <li> <a href="%(feed_url)s" title="subscribe"><img src="/pub.d/img/feed-icon-10x10.png" alt="(feed)"> All feeds in one</a></li>
            <li> <a href="%(opml_url)s" title="subscribe"><img src="/pub.d/img/feed-icon-10x10.png" alt="(feed)"> All feeds as OPML</a></li>
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

class About(HTML_Jinja_Template):
   def __init__(self, interpolate):
      HTML_Jinja_Template.__init__(self, interpolate, "about.html")
      self.interpolate['title'] = 'About'

class Index(HTML_Jinja_Template):
   def __init__(self, interpolate):
      HTML_Jinja_Template.__init__(self, interpolate, "index.html")
   def _render(self):
      o = self.interpolate
      for field in ['error', 'direc', 'subdirectory', 'turing']:
         if not field in self.interpolate:
            self.interpolate[field] = ''
      template = JinjaEnv.get_template(self.template_fname)
      if o['base_href'] == '/':
         o['domain'] = "Your planet URL will be on this website in the subdirectory you specify,"
      else:
         o['domain'] = "Your planet URL will be %(base_href)ssubdirectory," % o
      return template.render(**o)

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
            o['rendered_image'] = '<img class="face" src="/pub.d/img/silhouette2.png" />\n'
         s += """
		<tr class="%(row_class)s" id="feed_row%(idx)s">
                  <td style="vertical-align:middle" class="entrytitleauthor">
                      %(rendered_image)s
                  </td>
		  <td style="text-align:left">
		    <input type="hidden" name="section%(idx)s" id="section%(idx)s" value="%(section)s" />
		    <input type="hidden" name="delete%(idx)s" id="delete%(idx)s" value="0" />
		    <a href="javascript:rm_feed(%(idx)s)"><img class="feedbtn" src="/pub.d/img/rm-feed.png"></a> <label for="name%(idx)s">Feed Name:</label><br />
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
        <div class="entrytitle">Feeds <a href="javascript:add_feed()"><img src="pub.d/img/add-feed.png" width="14" height="14" border="0" alt="Add new feed button" name="AddFeedBtn" class="feedbtn"></a></div>
	<p>Use the <a href="javascript:add_feed()"><img src="pub.d/img/add-feed.png" width="14" height="14" border="0" alt="Add new feed button" name="AddFeedBtn" class="feedbtn"></a> and <img src="pub.d/img/rm-feed.png" width="14" height="14" border="0" alt="Remove feed sample" class="feedbtn"> buttons to add and remove feeds.</p>
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

