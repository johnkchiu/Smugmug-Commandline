Smugmug-Commandline
===================

A commandline interface for executing some tasks against Smugmug.

(This is built on the work done by https://github.com/chrishoffman/smugpy).

Installation
============
To use it, you must first install smugpy.  Then afterward, just downoad the script, make it executable, and use it.
```
$ wget https://raw.github.com/johnkchiu/Smugmug-Commandline/master/smugmugCommandline.py
$ chmod a+x smugmugCommandline.py
```

Usage
=====
Usage: 
  Commandline tool for Smugmug.
		smugmugCommandline.py [option]

Options:
  --version       show program's version number and exit
  -h, --help      show this help message and exit
  -a API_KEY      Smugmug API Key
  -e EMAIL        Login email
  -p PASSWORD     Login password
  -t TEMPLATE     Template name
  -c CATEGORY     Category name
  -s SUBCATEGORY  Sub-Category name
  -f FOLDER       Folder to upload from (should not have "/" at the end.

Example
=======
$ ./smugmugCommandline.py -a [XXX] -e [XXX] -p [XXX] -t 'My Defaults' -c Other -s Testing -f ~/Pictures/2012\ -\ 08\ -\ Mike\'s\ Vegas\ Trip