#!/bin/sh

# Run from parent directory as test/nose.sh
#
# Without any params, it uses some default params to get coverage.
# With params, it doesn't clutter the screen with coverage.  To do all
# tests and avoid the coverage report, do `test/nose.sh .`

if [ "$#" -eq 0 ]; then
    nosetests --cover-package=admin --cover-package=config --cover-package=galaxy --cover-package=new_planet --cover-package=planeteria --cover-package=planet --cover-package=templates --cover-package=util --with-coverage "$@"
else
    nosetests "$@"
fi