> Usage: episode-filer.py [options] FILE/DIR
> 
> episode-filer organizes your tv shows!
> 
> Options:
>   --version             show program's version number and exit
>   -h, --help            show this help message and exit
>   -p, --pretend         do not actually move any files, just show what would
>                         have happened
>   -b DIR, --base=DIR    use DIR as sorting base
>   -r, --recursive       if passing in a directory, recursively look for files.
>   -v, --verbose         be more verbose.
>   -e EXTENSIONS, --extensions=EXTENSIONS
>                         filter by this set of extensions, comma delimited.
>                         Default is .avi,.mkv.  If "*", all files will be
>                         examined.
>   --interactive     Ask before moving each file.  Default is False.

It appears to be fully functional, but it doesn't have any tests.  I'll be working on that shortly.

episode-filer assumes a heirarchy of base/TV Show Name/Season N/filename.avi.
It assumes the input files will have the show name in the beginning of the name and then the episode and season information.

Instructions
============
To sort a file, you'll need to do a little preparation on your directory tree.

First, you'll need some sort of base directory.
	ex: /vault/public/tv
Then, you'll need subdirectories in base to be named after TV shows, like Fringe or The Big Bang Theory.
	ex: /vault/public/tv/Fringe
	ex: /vault/public/tv/Big\ Bang\ Theory
episode-filer will use the beginning of the to-be-sorted file as a clue to which TV show it is.  You can give episode-filer guidance on this by adding a .names file inside the TV show directory.
	ex: /vault/public/tv/Sarah\ Jane\ Adventures/.names

You can then run episode-filer on some files, and if you point them to a base, it will try to move them to the right space.

Here's some samples to show off how nifty the filename parsing is:
> episode-filer.py --pretend --base /vault/public/tv /vault/public/unsorted/
>
> Filename: /vault/public/unsorted/heroes.308.hdtv-lol.avi
> Show: heroes, Season: 3, Episode: 8
> Would move /vault/public/unsorted/heroes.308.hdtv-lol.avi to /vault/public/tv/Heroes/Season 3
> 
> Filename: /vault/public/unsorted/The.Office.S05E02.HDTV.XviD-LOL.[VTV].avi
> Show: the office, Season: 5, Episode: 2
> Would move /vault/public/unsorted/The.Office.S05E02.HDTV.XviD-LOL.[VTV].avi to /vault/public/tv/The Office (US)/Season 5
> 
> Filename: /vault/public/unsorted/the_big_bang_theory.2x09.the_white_asparagus_triangulation.hdtv_xvid-fov.avi
> Show: the big bang theory, Season: 2, Episode: 9
> Would move /vault/public/unsorted/the_big_bang_theory.2x09.the_white_asparagus_triangulation.hdtv_xvid-fov.avi to /vault/public/tv/Big Bang Theory/Season 2

However, the current version of episode-filer cannot perform magic.  This is what it looks like when episode-filer cannot parse a filename.

> Unable to parse /vault/public/unsorted/The Best Of Christopher Walken.avi

Parsing Filenames
=================
episode-filer uses the XBMC regexes to get the season and episode information from a filename.  It then takes the part of the filename that comes before the season and episode information as the name.  To account for minor changes in the name, it cleans the name up into a "clean TV show name".

Clean TV Show Names
===================
The rules for what make up a clean TV show name is inside of tvorg's clean_tv_show() function.

The rules are as follows:
* Turn all _'s and .'s into spaces.
* Make the name lowercase, and then remove any whitespace from the beginning or end.
* If the name ends with " -", remove it.

Some example:
    >>> clean_show_name('The.IT.Crowd.')
    'the it crowd'

    >>> clean_show_name('Doctor Who - ')
    'doctor who'

    >>> clean_show_name('Coupling ')
    'coupling'

    >>> clean_show_name('heroes_')
    'heroes'

    >>> clean_show_name('the_big_bang_theory.')
    'the big bang theory'

.names Files
============
Without a .names file, only files that have the same "clean TV show name" as the directory's "clean TV show name" will be placed in that diretory.

If you put a file called .names inside a TV show directory, it will use each line's contents as a possible "clean TV show name" for that directory.  It will no longer use the "clean TV show name" of the directory, so if you want that name as an optoin, include it in the .names file.

If you have a top-level directory inside of base that you do not want anything sorted into, you can place an empty .names file into the directory, or a .names file where every line begins with a #.

Some examples:

I have a directory in my base called Doctor Who.  That's for *old* Doctor Who, and it has DVD images in it.  Nothing ever should get automatically sorted into this directory.  I also have a directory in my base called Doctor Who (2005).  That is for the new series.  However, some files that should get autofiled in Doctor Who (2005) have a "clean tv show name" of doctor who.  If I don't tell episode-filer to ignore Doctor Who, I will get new episodes autofiled into the old directory.  I fix this with the following .names files.

"/vault/public/tv/Doctor Who/.names":
#ignore
"/vault/public/tv/Doctor Who (2005)/.names":
doctor who
doctor who 2005
doctor who 2006
doctor who 2007
dr who
drwho2007

Some more examples:

"/vault/public/tv/Avatar/.names":
avatar
avatar - the last airbender
avatar the last airbender

"/vault/public/tv/Battlestar Galactica/.names":
battlestar galactica
bsg

Using names-detector to create .names files
===========================================
There's also a helper program names-detector.

> Usage: names-detector.py [options]
>     
> names-detector.py scans the specified directory for tv show files.  It will print out a
> summary of the "clean tv show names" of the files it can parse.

> Options:
>   --version             show program's version number and exit
>   -h, --help            show this help message and exit
>   -d DIRECTORY, --directory=DIRECTORY
>                         scan DIRECTORY (defaults to current directory)

Example usage:

> wolf@danny:/vault/public/tv/Battlestar Galactica$ ~/project/episode-filer/names-detector.py 
> battlestar galactica
> bsg

Troubleshooting, Questions, or Comments:
========================================
Feel free to contact me at http://feelslikeburning.com/contact
