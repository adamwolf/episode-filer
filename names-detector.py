#!/usr/bin/env python
"""
names-detector.py
Detect "clean tv show names" of any tv show files it can parse from the
specified directory.

Adam Wolf
http://feelslikeburning.com
"""

import tvorg, logging
import os
from optparse import OptionParser
import sys

version = "%prog 0.1"

def parse_commandline():
    """Returns a tuple (options, args) from OptionParser and does any error handling."""
    logging.debug("Parsing command line")
    usage = """usage: %prog [options]
    
%prog scans the specified directory for tv show files.  It will print out a
summary of the "clean tv show names" of the files it can parse."""
    parser = OptionParser(usage, version=version)
    parser.add_option("-d","--directory", help="scan DIRECTORY (defaults to current directory)", metavar="DIRECTORY", dest="directory", default=os.getcwd())
    (options, args) = parser.parse_args()
    return options, args

def main():
    logging.debug("started")
    (options, args) = parse_commandline()
    logging.debug("Parsed Options: %s" % options)
    logging.debug("Parsed Arguments: %s" % args)

    names = set()

    for root, dirs, files in os.walk(options.directory):
        for file in files:
            logging.debug("Parsing show information from %s" % file)
            info = tvorg.get_info_for_file(os.path.split(file)[1])
            if info:
                show, season, episode = info
                logging.debug("show: %s, season: %s, episode: %s" % info)
                names.add(show)

    for name in sorted(names):
        print name

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
