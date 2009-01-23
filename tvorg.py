#!/usr/bin/env python
"""tvorg.py
tvorg.py is a library for organizing tv shows.  It's used by episode-filer and
names-detector.

Adam Wolf
http://feelslikeburning.com
"""

import re

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
