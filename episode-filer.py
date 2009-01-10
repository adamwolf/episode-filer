#!/usr/bin/env python
"""
episode-filer.py

episode-filer organizes your tv shows!  

Adam Wolf
http://feelslikeburning.com
"""

import tvorg, logging, os, sys, shutil
from optparse import OptionParser


def parse_commandline():
    """Returns a tuple (options, args) from OptionParser and does any error handling."""
    usage = "usage: %prog [options] FILE/DIR"
    parser = OptionParser(usage, version="%prog 0.1")
    parser.add_option("-p", "--pretend", help="do not actually move any files, just show what would have happened", action="store_true", dest="pretend")
    parser.add_option("-c", "--config-file", help="use FILE as configuration file", metavar="FILE", default="~/.tvsorter", dest="config_file")
    parser.add_option("-b", "--base", help="use DIR as sorting base", metavar="DIR", dest="base")
    parser.add_option("-r", "--recursive", help="if passing in a directory, recursively look for files.", dest="recursive", default=False, action="store_true")
    parser.add_option("-v", "--verbose", action="count", dest="verbosity", help="be more verbose.")
    parser.add_option("-e", "--extensions", dest="extensions", help="filter by this set of extensions, comma delimited.  Default is %default.  If \"*\", all files will be examined.", default=".avi,.mkv")
    parser.add_option("-c", "--copy", dest="copy", help="copy files instead of moving them.", action="store_true")
    (options, args) = parser.parse_args()
    if not options.base:
        parser.error("--base must be specified.")
    if not os.path.exists(options.base):
        parser.error("base %s doesn't exist." % options.base)
    if not args:
        parser.error("no files or directories passed for sorting.")
    if options.extensions != "*":
        options.extensions = [extension for extension in options.extensions.split(",")]
    
    if options.verbosity == 1:
        logging.getLogger('').setLevel(logging.DEBUG)

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
        for directory in directories:
            for root, dirs, file_list in os.walk(directory):
                for file in file_list:  
                    files.append(os.path.join(root, file))
    else:
        for directory in directories:
            for entry in os.listdir(directory):
                pathname = os.path.join(directory, entry)
                if os.path.isfile(pathname):
                    files.append(pathname)

    logging.debug("files: %s" % files)
   
    #this should be done in the main loop of file adding
    #but I pasted it in from main()
    if options.extensions != "*":
        logging.debug("pruning file list.  using extensions: %s" % options.extensions)
        files_by_extension = {}
        for extension in options.extensions:
            files_by_extension[extension] = [file for file in files if file.endswith(extension)]
        files = []
        for extension, file_list in files_by_extension.items():
            files.extend(file_list)
    else:
        logging.debug("No files pruned because * passed in as extension list")

    return files

def get_show_names(base):
    """Detects show names"""
    show_names = {}
    logging.debug("Detecting show names from .names files")
    for show in os.listdir(base):
        if ".names" in os.listdir(os.path.join(base, show)):
            logging.debug("found %s" % os.path.join(base, show, ".names"))
            name_file = open(os.path.join(base, show, ".names"))
            show_names[show] = [line.strip() for line in name_file if not line.startswith("#")]
            #test that if you have only a #ignore line in your .names directory
            #it will ignore that directory
            name_file.close()
        else:
            #if you didn't find a name file, add the clean name of the directory
            #as the name of the show.
            show_names[show] = tvorg.clean_show_name(show)
        
        logging.debug("found alternate names %s for %s" % (show_names[show], show))

    return show_names

def move_file(file, directory, season, options):
    """Move tv show into directory inside of options.base.  If options.pretend,
    don't actually do anything, just splatter logging with it."""
    
    filename = os.path.split(file)[1]
    
    if options.pretend:
        logging.debug("not actually going to move %s because options.pretend is set." % file)
    logging.debug("trying to move %s" % file)

    #oh noes! what if season is something tricky like ../../../../../../?
    #um, how about I finally learn Template and be done with it?
    season_name = "Season %s" % int(season)

    show_dir = os.path.join(options.base, directory)
    dest_dir = os.path.join(show_dir, season_name)
    dest_file = os.path.join(dest_dir, filename)
    logging.debug("destination file: %s" % dest_file)

    if not os.path.exists(show_dir):
        logging.error("top level show directory %s doesn't exist in base directory %s. moving on." % (directory, options.base))
        return

    if not os.path.exists(dest_dir):
        logging.info("Season directory %s doesn't exist in %s." % (season_name, show_dir))
        if not options.pretend:
            logging.info("Creating %s" % dest_dir)
            os.mkdir(dest_dir)
    
    if os.path.exists(dest_file):
        logging.error("file called %s already in destination %s.  leaving %s alone." % (filename, dest_dir, file))
        return
    
    logging.debug("wheew.  actually passed all those tests, and now we're going to move the file.")
    if not options.pretend:
        logging.info("Moving %s to %s" % (file, dest_dir))
        shutil.move(file, dest_file)
        #os.system("touch \"%s\"" % dest_file)
    else:
        logging.debug("not really, of course, because we're only pretend!")
        
        
def main():
    """Moves specified files to an organized location based on filenames."""
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
            logging.info("Filename: %s" % file)
            logging.info("Show: %s, Season: %s, Episode: %s" % info)
            directory = False

            for tv_show in show_names:
                if show in show_names[tv_show]:
                    directory = tv_show
                    break
            
            if directory:
                logging.debug("directory %s found for %s" % (os.path.join(options.base, directory), show))
                move_file(file, directory, season, options)
            else:
                logging.error("Directory not found for %s from filename %s" % (show, file))

        else:
            logging.info("Unable to parse %s" % file)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
