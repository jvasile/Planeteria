import unittest, copy
from galaxy import Galaxy
from new_planet import *

## Remove console logger to avoid clutter (see planeteria log instead)
for h in log.handlers:
    if h.get_name() == "planeteria console logger":
        log.removeHandler(h)

class validate_input_test(unittest.TestCase):
    def usual_case_test(s):
        assert validate_input("good_name45")

    def badchars_test(s):
        assert not validate_input("http://planeteria.org/ICannotFollowDirections")

    def spaces_test(s):
        assert not validate_input("planet name should not have spaces")

    def apostrophe_test(s):
        assert not validate_input("planet_name_shouldn't_have_an_apostrophe")


class make_planet_test(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        galaxy = Galaxy(['nosetest'])
        galaxy.load()
        nosetest = galaxy.get_planet_by_subdir("nosetest")
        if nosetest:
            nosetest.delete()

    def make_planet_test(s):
        make_planet("nosetest")
        s.assertTrue(os.path.exists(os.path.join(opt['output_dir'],"nosetest")))
        
        files = os.listdir(os.path.join(opt['output_dir'],"nosetest"))
        s.assertTrue('admin.py'  in files)
        s.assertTrue('index.html' in files)
        s.assertTrue('pub.d' in files)

    @classmethod
    def teardown_class(cls):
        galaxy = Galaxy(['nosetest'])
        galaxy.load()
        nosetest = galaxy.get_planet_by_subdir("nosetest")
        if nosetest:
            nosetest.delete()
        
