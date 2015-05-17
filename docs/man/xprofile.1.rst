.. -*- rst -*-

========
xprofile
========

--------------------------------------------------------------
A tool to manage and automatically apply xrandr configurations
--------------------------------------------------------------

:Author: Nico Di Rocco <dirocco.nico@gmail.com>
:Date: 2015-05-17
:Copyright: GPLv3
:Version: 1.2.0
:Manual section: 1


SYNOPSIS
========
**xprofile** [--verbose] [--config CONFIG] *subcommand*


OPTIONS
=======
-h, --help            show this help message and exit
--verbose             output more verbosely
--config CONFIG       config file to read profiles from
--version             show program's version number and exit


SUBCOMMANDS
===========
list
    list all available xrandr profiles

current
    get information about the current active profile

generate
    generate a new profile and print to stdout

activate
    activate the given profile or automatically select one


DESCRIPTION
===========
**xprofile** TODO: edit this


CONFIGURATION
=============
By default, **xprofile** reads *~/.xprofilerc*.  The configuration file is used
to store xrandr profiles so they can be applied later.

The location of the configuration file can be configured using the
*-c|--config* command line options.

**xprofile** can automatically write new profiles to this configuration but if
you wish you can manually edit this configuration file. For details on how to
write **xprofile** configuration files refer to **xprofilerc**\(5)


SEE ALSO
========
**xprofilerc**\(5), **xrandr**\(1)


BUGS
====
**xprofile** might not support every xrandr configuration options.


CHANGELOG
=========
.. include:: ../../CHANGELOG.rst
   :start-line: 4
