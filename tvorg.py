#!/usr/bin/env python
"""tvorg.py
tvorg.py is a library for organizing tv shows.  It's used by episode-filer and
names-detector.

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

import re, os.path

class Episode():
    def __init__(self, path=None):
        self.path = path
        self.filename = os.path.split(path)[1]
        self.parsed_show, self.parsed_season, self.parsed_episode = parse_filename(self.filename)

    def __str__(self):
        return "%s - Season %i, Episode %i" % (self.parsed_show,
                self.parsed_season, self.parsed_episode)

class Show():
    def __init__(self, directory=None, name=None, names=None):
        self.directory = directory
        self.name = name
        if names:
            self.names = set(names)
        else:
            self.names = set([name])

    def __str__(self):
        return self.name

    def add_name(self, name):
        self.names.add(name)
    
    def add_names(names):
        for name in names:
            self.add_name(name)

def clean_show_name(name):
    """This sanitizes a show name a little bit.

    >>> clean_show_name("The.IT.Crowd.")
    'the it crowd'

    >>> clean_show_name("Doctor Who - ")
    'doctor who'

    >>> clean_show_name("Coupling ")
    'coupling'

    >>> clean_show_name("heroes_")
    'heroes'

    >>> clean_show_name("the_big_bang_theory.")
    'the big bang theory'
    """
    name = re.sub("_", " ", name)
    name = re.sub("\.", " ", name)
    name = name.lower().strip()
    if name.endswith(" -"):
        name = name[0:len(name)-2]
    return name

def parse_filename(filename):
    """This returns the show, season, and episode number for a single file.

    >>> parse_filename("The.IT.Crowd.S03E06.WS.PDTV.XviD-RiVER.avi")
    ('the it crowd', 3, 6)
    
    """
    file_regex_sources = [r'\[[Ss]([0-9]+)\]_\[[Ee]([0-9]+)([^\\/]*)', 
            r'[\._ \-]([0-9]+)x([0-9]+)([^\\/]*)', 
            r'[\._ \-][Ss]([0-9]+)[\.\-]?[Ee]([0-9]+)([^\\/]*)', 
            r'[\._ \-]([0-9]+)([0-9][0-9])([\._ \-][^\\/]*)',] 
 
    file_regexes = [] 
    for file_regex_source in file_regex_sources: 
        file_regexes.append(re.compile(file_regex_source)) 
    
    for file_regex in file_regexes: 
        match = file_regex.search(filename) 
        if match: 
            break 
    if not match:
        raise NameError, "Cannot parse %s" % filename
    else:
        season = int(match.group(1))
        episode = int(match.group(2))
        show = filename[0:match.start()] 
        show = clean_show_name(show)
        return (show, season, episode)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
