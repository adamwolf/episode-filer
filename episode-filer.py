#!/usr/bin/env python
import tvorg, logging
import os
from optparse import OptionParser
import ConfigParser
import sys

version = "%prog 0.1"

def parse_commandline():
    """Returns a tuple (options, args) from OptionParser and does any error handling."""
    logging.debug("Parsing command line")
    usage = "usage: %prog [options] argument"
    parser = OptionParser(usage, version=version)
    parser.add_option("-p","--pretend", help="do not actually move any files, just show what would have happened", action="store_true", dest="pretend")
    parser.add_option("-c","--config-file", help="use FILE as configuration file", metavar="FILE", default="~/.tvsorter", dest="config_file")
    parser.add_option("-b","--base", help="use DIR as sorting base", metavar="DIR", dest="base")
    parser.add_option("-r","--recursive", help="if passing in a directory, recursively look for files.", dest="recursive", default=False, action="store_true")
    (options, args) = parser.parse_args()
    if not options.base:
        parser.error("--base must be specified. Exiting.")
    return options, args

def get_file_list(options, args):
    """Returns a list of files to be sorted based on the options and
    arguments."""

    files = []
    directories = []

    for arg in args:
        arg = os.path.expanduser(arg)
        if os.path.isfile(arg):
            files.append(arg)
        if os.path.isdir(arg):
            directories.append(arg)

    if options.recursive:
            logging.debug("recursive")
            for directory in directories:
                for root, dirs, file_list in os.walk(directory):
                    logging.debug(root)
                    logging.debug(file_list)
                    for file in file_list:
                        files.append(os.path.join(root, file))
    else:
            logging.debug("not recursive")
            for directory in directories:
                for entry in os.listdir(directory):
                    pathname = os.path.join(directory, entry)
                    if os.path.isfile(pathname):
                        files.append(pathname)

    logging.debug("files: %s" % files)

    return files

def get_show_names(base):
    """Detects show names"""
    show_names = {}
    logging.debug("Detecting show names from .names files")
    for show in os.listdir(base):
        if ".names" in os.listdir(os.path.join(base, show)):
            logging.debug("found %s" % os.path.join(base, show, ".names"))
            f = open(os.path.join(base, show, ".names"))
            show_names[show] = [line.strip() for line in f if not line.startswith("#")]
            f.close()
        else:
            show_names[show] = tvorg.clean_show_name(show)
        
        logging.debug("found alternate names %s for %s" % (show_names[show], show))

    return show_names

def main():
    logging.debug("started")
    (options, args) = parse_commandline()
    logging.debug("Parsed Options: %s" % options)
    logging.debug("Parsed Arguments: %s" % args)

    files = get_file_list(options, args)
    
    if not files:
        logging.critical("No files found to sort! Exiting.")
        sys.exit(1)

    show_names = get_show_names(options.base)
    logging.debug("Show names: %s" % show_names)

    for file in files:
        logging.debug("Parsing show information from %s" % file)
        info = tvorg.get_info_for_file(os.path.split(file)[1])
        if info:
            show, season, episode = info
            logging.debug("show: %s, season: %s, episode: %s" % info)
            directory = False

            for tv_show in show_names:
                if show in show_names[tv_show]:
                    directory = tv_show
                    break
            if not directory:
                logging.error("directory not found for %s from filename %s " % (show, file))
            else:
                #we know where we should put it
                logging.debug("directory for %s found: %s" % (show, directory))

    
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
