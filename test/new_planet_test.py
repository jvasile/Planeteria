import unittest, copy
from galaxy import Galaxy
from new_planet import *
from nose.tools import raises

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
        make_planet("nosetest")

    def make_planet_test(s):
        s.assertTrue(os.path.exists(os.path.join(opt['output_dir'],"nosetest")))

    def make_planet_test_skel_links(s):
        files = os.listdir(os.path.join(opt['output_dir'],"nosetest"))
        s.assertTrue('admin.py' in files and 'pub.d' in files)

    def make_planet_test_skel_files(s):
        files = os.listdir(os.path.join(opt['output_dir'],"nosetest"))
        s.assertTrue('index.html' in files)

    @raises(BadSubdirNameError)
    def invalid_subdir_test(s):
        subdir = "planet name should not have spaces"
        galaxy = Galaxy([subdir])
        galaxy.load()
        p = galaxy.get_planet_by_subdir("nosetest")
        if p:
            p.delete()

        make_planet(subdir)

        galaxy = Galaxy(["planet name should not have spaces"])
        galaxy.load()
        p = galaxy.get_planet_by_subdir("nosetest")
        if p:
            p.delete()

        
    @classmethod
    def teardown_class(cls):
        galaxy = Galaxy(['nosetest'])
        galaxy.load()
        nosetest = galaxy.get_planet_by_subdir("nosetest")
        if nosetest:
            nosetest.delete()
        
