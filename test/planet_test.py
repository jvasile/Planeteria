import unittest
import os, shutil, glob
import config as cfg
from config import opt
log = cfg.logging.getLogger('planeteria')
from util import our_db, log
from planet import Planet
from new_planet_test import make_temp_planet, destroy_temp_planet
from validate_test import validate_p
from nose.tools import raises

feed_dir = os.path.join("test", "problem_feeds")

class add_feed_test(unittest.TestCase):
    name = "test_add_feed"
    url = os.path.join(feed_dir, "only_old_entries.rss")
    image = "http://image.url"
    user = "Doc Test"
    @classmethod
    def setup_class(cls):
        p = make_temp_planet(cls.name, get_planet=True)
        p.add_feed(cls.url, cls.user, cls.image, save=True)
        cls.planet = Planet(direc=cls.name)

    def test_add_feed(self):
        assert(self.url in self.planet.feeds)

    def test_add_feed_feedurl(self):
        assert(self.url in self.planet.feeds[self.url]['feedurl'])

    def test_add_feed_image(self):
        assert(self.image in self.planet.feeds[self.url]['image'])

    def test_add_feed_name(self):
        assert(self.user in self.planet.feeds[self.url]['name'])

    @classmethod
    def teardown_class(cls):
        destroy_temp_planet(cls.name)

def remove_direc_contents(direc):
    r = glob.glob(direc)
    for i in r:
        os.remove(i)

def ensure_generate_wrote_files(direc):
    files = os.listdir(direc)
    assert("index.html" in files)
    assert("atom.xml" in files)
    assert("opml.xml" in files)


def gen_temp_planet(feed):
    name = feed.split(".")[0] if '.' in feed else feed
    p = make_temp_planet(name, True)
    p.add_feed(os.path.join(feed_dir, feed), feed)
    remove_direc_contents(os.path.join(opt['output_dir'], p.direc, "*"))
    p.generate()
    return name

## Check Problem Feeds
def test_problem_feed_generation():
    for feed in os.listdir(feed_dir):
        yield check_generate_feed, feed
def check_generate_feed(feed):
    name = gen_temp_planet(feed)
    ensure_generate_wrote_files(os.path.join(opt['output_dir'],name))
    destroy_temp_planet(name)
    
@unittest.skip("not ready to validate atom")
def test_valid_atom():
    for feed in os.listdir(feed_dir):
        yield check_valid_atom, feed
def check_valid_atom(feed):
    name = gen_temp_planet(feed)
    assert(validate_p(os.path.join(opt['output_dir'], name, "atom.xml"), "A"))
    destroy_temp_planet(name)

@unittest.skip("not ready to validate opml")
def test_valid_opml():
    for feed in os.listdir(feed_dir):
        yield check_valid_atom, feed
def check_valid_opml(feed):
    name = gen_temp_planet(feed)
    assert(validate_p(os.path.join(opt['output_dir'], name, "opml.xml"), "A"))
    destroy_temp_planet(name)

@unittest.skip("not ready to do strict validation")
def test_strict_atom():
    for feed in os.listdir(feed_dir):
        yield check_valid_atom, feed
def check_strict_atom(feed):
    name = gen_temp_planet(feed)
    assert(validate_p(os.path.join(opt['output_dir'], name, "atom.xml"), "AA"))
    destroy_temp_planet(name)

@unittest.skip("not ready to do strict validation")
def test_strict_opml():
    for feed in os.listdir(feed_dir):
        yield check_valid_atom, feed
def check_strict_opml(feed):
    name = gen_temp_planet(feed)
    assert(validate_p(os.path.join(opt['output_dir'], name, "opml.xml"), "AA"))
    destroy_temp_planet(name)



class delete_test(unittest.TestCase):

    @raises(KeyError)
    def delete_test(s):
        name = "delete_test"
        p = make_temp_planet(name, True)
        p.delete()
        p = Planet(direc=name)

    @raises(KeyError)
    def already_deleted_test(s):
        name = "delete_test"
        p = make_temp_planet(name, True)
        p.delete()
        p.delete()
        p = Planet(direc=name)

    @raises(KeyError)
    def missing_on_disk_test(s):
        name = "delete_test"
        p = make_temp_planet(name, True)
        shutil.rmtree(os.path.join(opt['output_dir'], name))
        p.delete()
        p = Planet(direc=name)

    @raises(KeyError)
    def not_in_db_test(s):
        name = "delete_test"
        p = make_temp_planet(name, True)
        with our_db('planets') as db:
            del db[name]
        p.delete()
        p = Planet(direc=name)
    


