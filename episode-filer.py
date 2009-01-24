#!/usr/bin/env python
"""
episode-filer.py

episode-filer organizes your tv shows!  

http://feelslikeburning.com/projects/episode-filer/
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



import tvorg, logging, os, sys, shutil
from optparse import OptionParser

def parse_commandline():
    """Returns a tuple (options, args) from OptionParser and does any error handling."""
    usage = "usage: %prog [options] FILE/DIR"
    parser = OptionParser(usage, version="%prog 0.1")
    parser.add_option("-p", "--pretend", help="do not actually move any files, just show what would have happened", action="store_true", dest="pretend")
    parser.add_option("-b", "--base", help="use DIR as sorting base", metavar="DIR", dest="base")
    parser.add_option("-r", "--recursive", help="if passing in a directory, recursively look for files.", dest="recursive", default=False, action="store_true")
    parser.add_option("-v", "--verbose", action="count", dest="verbosity", help="be more verbose.")
    parser.add_option("-e", "--extensions", dest="extensions", help="filter by this set of extensions, comma delimited.  Default is %default.  If \"*\", all files will be examined.", default=".avi,.mkv")
    parser.add_option("-i", "--interactive", dest="interactive", action="store_true",
            help="Ask before moving each file.  Default is %default.",
            default=False)
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

def get_files(options, args):
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

def get_show_for_episode(episode, shows):
    for show in shows:
        if episode.parsed_show in show.names:
            return show


def get_shows(base):
    """Parses the directory tree and .names files to get a list of Shows."""
    shows = []
    logging.debug("Detecting shows from .names files")
    logging.debug(base)
    for directory in os.listdir(base):
        show_path = os.path.join(base, directory)
        if ".names" not in os.listdir(show_path):
            #if you didn't find a name file, add the clean name of the directory
            #as the name of the show.
            show = tvorg.Show(directory=show_path, name=tvorg.clean_show_name(directory))
            shows.append(show)
        else:
            names_path = os.path.join(show_path, ".names")
            logging.debug("found %s" % names_path)
            name_file = open(names_path)
            show_names = [line.strip() for line in name_file if not line.startswith("#")]
            name_file.close()
            if not show_names:
                #there were either no lines, or it was all comments / ignore
                #so we don't want to add it
                pass
            else:
                show = tvorg.Show(directory=show_path, name=tvorg.clean_show_name(directory), names=show_names)
                shows.append(show)
    return shows

        
def get_directory_from_show_names(show, show_names):
        for tv_show in show_names:
            if show in show_names[tv_show]:
                return tv_show
        return False

def get_interactive_response(episode, destination_path):
    stop = False
    response = False
    while not stop:
        response =  raw_input("Move %s to %s (y/n)? "% (episode.path, destination_path))
        if response != "y" and response != "n":
            print "Please respond with y or n."
        else:
            stop = True
    if response == "y":
        return True
    else:
        return False

def really_move(source, destination):
    """Really moves file source to file destination.  The only safety check it
    makes is to see if destination file exists.  Any directories needed are
    created."""
    
    if os.path.exists(destination):
        logging.info("%s already exists.  Not moving %s" % (destination, source))
    else:
        destination_directory = os.path.split(destination)[0]
        if not os.path.exists(destination_directory):
            logging.debug("creating directories to create %s" % destination_directory)
            os.makedirs(destination_directory)
        logging.info("Moving %s to %s." % (source, destination))
        shutil.move(source, destination)

def move_file(episode, show, options):
    
    if not os.path.isdir(show.directory):
        logging.error("Directory %s not found for TV show \"%s\"!" % (show.directory, show.name))
        return

    season_dir_name = "Season %i" % episode.parsed_season
    season_dir = os.path.join(show.directory, season_dir_name)
    destination_path = os.path.join(season_dir, episode.filename)

    if options.interactive:
        logging.debug("Querying user about move in terminal")
        if get_interactive_response(episode, destination_path):
            logging.debug("User said we should move file.")
        else:
            logging.debug("User said we shouldn't move file.")
            return

    if options.pretend:  
        #logging.info("Not moving because --pretend set.")
        return

    logging.debug("Really moving %s to %s" % (episode.path, destination_path))
    really_move(episode.path, destination_path)
    
def main():
    """Moves specified files to an organized location based on filenames."""
    logging.debug("Logging started.")
    (options, args) = parse_commandline()
    logging.debug("Parsed Options: %s" % options)
    logging.debug("Parsed Arguments: %s" % args)

    files = get_files(options, args)
            
    if not files:
        logging.critical("No files found to sort! Exiting.")
        sys.exit(1)

    shows = get_shows(options.base)
    
    for show in shows:
        logging.debug("%s" % show)
    
    for file in files:
        logging.debug("Parsing show information from %s" % file)
        try:
            episode = tvorg.Episode(path=file)
        except NameError, error:
            logging.info("Error while parsing file %s: %s" % (file, error))
            continue

        logging.info("\nFile: %s" % file)
        logging.info("Episode Information: %s" % episode)
        
        show = get_show_for_episode(episode, shows)
        if not show:
            logging.error("Show not found for TV show \"%s\" for file %s. Perhaps you need to create a directory in %s for this show. If you have a directory for this show, try adding the show name detected for this file to the .names file.\n" % (episode.parsed_show, file, options.base))
        else:
            move_file(episode, show, options)

    logging.debug("Completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
