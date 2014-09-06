xprofile
========
A tool to manage and automatically apply xrandr configurations.

.. image:: https://travis-ci.org/nrocco/xprofile.svg?branch=master
    :target: https://travis-ci.org/nrocco/xprofile


**xprofile** is compatible with and tested on python version 2.6, 2.7, 3.2, 3.3
and 3.4.


installation
------------
A universal installation method is to use pip (the pip package is available `here`_)::

    $ pip install --upgrade xprofile

Before installing **xprofile** with pip see if a package for your Operating
System exists.

To install **xprofile** for arch linux you can use the `AUR package`_::

    # This is an example using yaourt
    $ yaourt -S xprofile


usage
-----
Once `xprofile` has been installed you can execute the following command to get
some help::

    $ xprofile --help


To get detailed help for a specific subcommand use::

    $ xprofile [subcommand] --help


Or refer to the **xprofile**\(1) and **xprofilerc**\(5) man pages.


license
-------

**xprofile** is licensed under GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

    The GNU General Public License is a free, copyleft license for software and
    other kinds of works.

For the full license information refer to the `LICENSE`_ file in the github
repository.


.. _AUR package: https://aur.archlinux.org/packages/xprofile/
.. _here: https://pypi.python.org/pypi/xprofile
.. _LICENSE: https://github.com/nrocco/xprofile/blob/master/LICENSE
