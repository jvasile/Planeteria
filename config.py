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

opt={'base_href':BASE_HREF,
     'website_name':"Planeteria",
     'generator':"Planeteria %s" % VERSION,
     'generator_uri':"http://planeteria.org/copyright.html",
     'force_check': False,
     'template_dir':TEMPLATE_DIR
     }
