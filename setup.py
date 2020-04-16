
import os
import re

from setuptools import setup, find_packages

#------------------------------------------------------------------------------#
#                                                                              #
#------------------------------------------------------------------------------#

def extract_symbol(version_file, symbol):

    # __version__ = "...."
    # __version__ = '....'
    VSRE = r"^__%s__\s*=\s*['\"]([^'\"]*)['\"]" % (symbol)

    verstrline = open(version_file, "rt").read()

    mo = re.search(VSRE, verstrline, re.M)
    if not mo:
        raise RuntimeError("Unable to find %s string in %s." % (symbol, version_file,))

    return mo.group(1)

def get_version_from_file():
    try:
        f = open('VERSION')
        data = f.read()
        f.close()
        return data.strip()
    except Exception, e:
        return None
        
#------------------------------------------------------------------------------#
#                                                                              #
#------------------------------------------------------------------------------#

print "Reading version from file"
VERSION = get_version_from_file()
if not VERSION:
    print "Reading version from sourcecode"
    VERSION = extract_symbol('svmlib/__init__.py', 'version')

if not VERSION:
    raise Exception("Unable to get version")

print "Package version: ", VERSION
print "Found following packages:"
PACKAGES = find_packages()

for name in PACKAGES:
    print "\t", name


REQUIREMENTS = [
]

#------------------------------------------------------------------------------#
#                                                                              #
#------------------------------------------------------------------------------#

setup(
    name             = 'svmlib',
    version          = '0.1',
    description      = 'Simple Virtual Machine Library',

    packages         = PACKAGES,
    
    install_requires = REQUIREMENTS,

    # Metadata
    author           = 'Diego Billi',
    author_email     = 'diegobilli@gmail.com',
    url              = 'https://github.com/dbilli/svmlib',
    
    license          = "GPLv2",
)

#------------------------------------------------------------------------------#

