import unittest
import os
import planeteria
import config as cfg
from config import opt
log = cfg.logging.getLogger('planeteria')

class file_permission_test(unittest.TestCase):
    """Make sure file permissions allow us to run the various bits of
    code.  These should all be 755 or 775."""
    def get_perms(s, fname):
        return oct(os.stat(fname)[0])[-3:]
    def executable_p(s, mode):
        return mode == "775" or mode == "755"
    def planeteria_test(s):
        s.assertTrue(s.executable_p(s.get_perms("planeteria.py")))
    def admin_test(s):
        s.assertTrue(s.executable_p(s.get_perms("admin.py")))
    def planet_test(s):
        s.assertTrue(s.executable_p(s.get_perms("planet.py")))
    def new_planet_test(s):
        s.assertTrue(s.executable_p(s.get_perms("new_planet.py")))
    def nose_sh_test(s):
        s.assertTrue(s.executable_p(s.get_perms("test/nose.sh")))
