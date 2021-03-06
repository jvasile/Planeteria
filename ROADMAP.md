# Planeteria Project Road Map & Wishlist

This document lists known bugs & feature requests, and our plans/vision to address them.  

In January-April 2013, Aleta Dunne is working on Planeteria as a
project for her OPW internship; one goal of the internship is to build
community and momentum around this project so that it can continue to
be improved after the internship ends and Aleta has less time to
dedicate to Planeteria.

## IN PROGRESS

Website Redesign with Twitter Bootstrap
 * The redesign will modernize the code with HTML5 & jQuery, make the
   site friendly to mobile devices (responsive design), and make minor
   improvements to the UI and sitemap.
 * New feed tagging feature will allow planet readers to read the
   blogs in the feed that interest them most.

Addressing various bugs relating to proper parsing of feeds so that
they display correctly.  These are documented in the Github issue
tracker, https://github.com/jvasile/Planeteria/issues?state=open.

## ONGOING

Community-building around the project and individual planets

 * Spreading the word about Planeteria as an easy way to create new
   planets.
 * Promoting the Women in Free Software planet; continuing to curate
   the feed to make it useful and relevant to readers.
 * Create spaces for discussion about Planeteria.
    - Planeteria mailing list will be set up very soon for an archived
      discussion space.
    - Currently, much of the discussion about Planeteria happens on
    #opw channel on irc.gnome.org where @aleta can often be
    found.  This is a useful tool for real-time conversations and
    quick questions. If/when Planeteria discussion creates too much
    noise in that channel, we’ll create an IRC channel just for
    Planeteria discussion.

Improving site installation process & instructions to make it easy for
new contributors to get started. (We’d love help from contributors
with this)

## FUTURE PROJECTS

Aleta will drive these tasks, but will probably not be able to work on
them until after the internship period is over; it would be nice to
have contributors who can lend their expertise and help move the
progress forward more quickly.

 1. Adding OPML support for blog feeds
 2. Separate admin login and administrator contact information changes
 from feed changes in UI.
 3. Multiple logins for a single planet
 4. Planet-specific web analytics
 5. Automatic in-document feed updates using JSON
 6. Automating pulling inactive blogs from feeds

There is some discussion of adding social media integration; this
requires more discussion as to how it could be done in a way that is
useful to readers, without drowning out blog posts or cluttering the
UI.

## SYSADMIN TASKS FOR JAMES

 1. Adding an uptime monitoring service to help improve site uptime
 2. Increase cron job update frequency (5 mins?)
 3. Adding web analytics ( http://awstats.sourceforge.net/ )
 4. Moving the site to its own server (longer term goal)

