#!/usr/bin/env python
"""
names-detector.py
Detect "clean tv show names" of any tv show files it can parse from the
specified directory.

http://feelslikeburning.com/projects/episode-filer
"""
#    Copyright 2009 Adam Wolf
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



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
            try:
                episode = tvorg.Episode(path=file)
                logging.debug("%s" % episode)
                names.add(episode.parsed_show)
            except NameError, e:
                logging.debug("unable to parse %s: %s" % (file, e))

    for name in sorted(names):
        print name

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
