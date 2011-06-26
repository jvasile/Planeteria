import os


BASE_HREF = "file:///home/vasile/src/planeteria2/www/"
BASE_HREF = "http://test.planeteria.org/"
BASE_DIR = os.path.dirname(os.path.abspath( __file__ ))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "www")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CHECK_INTERVAL = 3600 # dload feed once per hour
VERSION = "2.1.0"
DATA_FORMAT_VERSION = "0.1.0"
CHECK_INTERVAL = 3600  # dload feed once per hour
MAX_ENTRIES = 100

opt={'domain':'test.planeteria.org',
     'base_href':BASE_HREF,
     'website_name':"Planeteria",
     'generator':"Planeteria %s" % VERSION,
     'generator_uri':"http://planeteria.org/copyright.html",
     'force_check': False,
     'template_dir':TEMPLATE_DIR,
     'new_planet_dir':os.path.join(TEMPLATE_DIR, "new_planet"),
     }

opt.update(locals())

import logging
logger = logging.getLogger('planeteria')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(BASE_DIR, 'planeteria.log'))
fh.setLevel(logging.DEBUG)


# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

