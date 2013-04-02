import unittest, subprocess
from galaxy import Galaxy
from new_planet import *
from nose.tools import raises

## Remove console logger to avoid clutter (see planeteria log instead)
for h in log.handlers:
    if h.get_name() == "planeteria console logger":
        log.removeHandler(h)

def run_twill_script(script):
    with open('test/twill.tmp', 'w') as OUTF:
        OUTF.write(script)
    ret = subprocess.call("twill-sh -q -u %s test/twill.tmp" % opt['base_href'], shell=True)
    os.unlink('test/twill.tmp')
    return ret

def destroy_temp_planet(planet_name):
    galaxy = Galaxy([planet_name])
    galaxy.load()
    p = galaxy.get_planet_by_subdir(planet_name)
    if p:
        p.delete()

def make_temp_planet(planet_name):
    destroy_temp_planet(planet_name)
    return make_planet(planet_name)

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
    def make_planet_test(s):
        make_temp_planet('nosetest')
        s.assertTrue(os.path.exists(os.path.join(opt['output_dir'],"nosetest")))
        destroy_temp_planet('nosetest')

    def make_planet_test_skel_links(s):
        make_temp_planet('nosetest')
        files = os.listdir(os.path.join(opt['output_dir'],"nosetest"))
        s.assertTrue('admin.py' in files and 'pub.d' in files)
        destroy_temp_planet('nosetest')

    def make_planet_test_skel_files(s):
        make_temp_planet('nosetest')
        files = os.listdir(os.path.join(opt['output_dir'],"nosetest"))
        s.assertTrue('index.html' in files)
        destroy_temp_planet('nosetest')

    def planet_exists_on_disk_but_not_in_db_test(s):
        destroy_temp_planet('nosetest1')
        path = os.path.join(opt['output_dir'],"nosetest1")
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        s.assertTrue(make_temp_planet('nosetest1'))
        destroy_temp_planet('nosetest1')

    @raises(BadSubdirNameError)
    def badchars_test(s):
        name = "http://planeteria.org/ICannotFollowDirections"
        make_temp_planet(name)
        destroy_temp_planet(name)

    @raises(BadSubdirNameError)
    def spaces_test(s):
        name = "planet name should not have spaces"
        make_temp_planet(name)
        destroy_temp_planet(name)

    @raises(BadSubdirNameError)
    def apostrophe_test(s):
        name = "planet_name_shouldn't_have_an_apostrophe"
        make_temp_planet(name)
        destroy_temp_planet(name)

class make_planet_gui_test(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        destroy_temp_planet("twilltest")
        # make twilltest planet via web interface
        script = """code 200
fv 1 turing yes
fv 1 subdirectory twilltest
submit 3
code 200
"""
        run_twill_script(script)

    def base_href_test(s):
        s.assertNotEqual(opt['base_href'], "/", "Must set base href to run gui tests.")

    def make_planet_test(s):
        s.assertTrue(os.path.exists(os.path.join(opt['output_dir'],"twilltest")))

    def make_planet_test_skel_links(s):
        files = os.listdir(os.path.join(opt['output_dir'],"twilltest"))
        s.assertTrue('admin.py' in files and 'pub.d' in files)

    def make_planet_test_skel_files(s):
        files = os.listdir(os.path.join(opt['output_dir'],"twilltest"))
        s.assertTrue('index.html' in files)

    def try_bad_subdir(s, subdir, turing=True, msg=None):
        if not msg:
            msg = "Subdirectory can only contain letters, numbers and underscores."
        script = """code 200
fv 1 turing %s
fv 1 subdirectory "%s"
submit 3
code 200
find "%s"
""" % ("yes" if turing else "no", subdir, msg)
        return run_twill_script(script)

    def badchars_test(s):
        name = "http://planeteria.org/ICannotFollowDirections"
        s.assertEqual(s.try_bad_subdir(name), 0)

    def spaces_test(s):
        name = "planet name should not have spaces"
        s.assertEqual(s.try_bad_subdir(name), 0)

    def apostrophe_test(s):
        name = "planet_name_shouldn't_have_an_apostrophe"
        s.assertEqual(s.try_bad_subdir(name), 0)

    def turing_test(s):
        name = "harmlessplanetname"
        s.assertEqual(s.try_bad_subdir(name, turing=False, msg="sociopath"), 0)

    @classmethod
    def teardown_class(cls):
        destroy_temp_planet("twilltest")
        
