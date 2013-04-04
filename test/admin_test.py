import unittest
import config as cfg
from config import opt
log = cfg.logging.getLogger('planeteria')
import admin
from util_test import twill
from new_planet_test import make_temp_planet, destroy_temp_planet

from selenium import webdriver

class admin_test(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.planet_name = "admin_test"
        cls.planet_url = opt['base_href']+cls.planet_name+"/"
        make_temp_planet(cls.planet_name)

        cls.browser = webdriver.Firefox()
    def admin_page_load_test(s):
        script = """code 200
#find "http://hackervisions.org/?feed=rss2"
"""
        s.assertEqual(twill(script, s.planet_url+"admin.py"), 0)

    @classmethod
    def teardown_class(cls):
        destroy_temp_planet(cls.planet_name)
        cls.browser.close()
