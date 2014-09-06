.. -*- rst -*-

==========
xprofilerc
==========

----------------------------------------------------
Configuration for xprofile, a xrandr profile manager
----------------------------------------------------

:Author: Nico Di Rocco <dirocco.nico@gmail.com>
:Date: 2014-09-05
:Copyright: GPLv3
:Version: 1.1.4
:Manual section: 5


SYNOPSIS
========
**xprofilerc**


DESCRIPTION
===========
**xprofile**\(1) uses a configation file to persist xrandr profiles. The
default location for this file is in the users `$HOME` directory at
`~/.xprofilerc`.

An xrandr profile should be defined like this::

    [study]
    name = my study at home
    edid = f1e5c600d38a9625f2b50df1b9aa7ba9
    args = --output LVDS1 --off --output HDMI2 --right-of LVDS1 --primary --output HDMI3 --right-of HDMI2

In the example above the profile identifier is *study*. This identifier can be
used in subcommands of **xprofile**\(1).  The various profile configuration
options explained:

name
    A more detailed name for this profile (not required)

edid
    Every profile will be given a unique identifier. The unique identifier is
    calculated by **xprofile**\(1) using the EDID information of all connected
    displays. The edid value in a profile section in `~/.xprofilerc` is a md5
    hash of this EDID information. With this unique edid hash the *auto*
    subcommand of **xprofile**\(1) is able to automatically select the right
    profile (required).

args
    These are the options passed directly to **xrandr**\(1) when a profile is
    activated.


SEE ALSO
========
**xprofile**\(1), **xrandr**\(1)
