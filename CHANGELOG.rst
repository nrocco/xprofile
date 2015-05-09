CHANGELOG
=========

All notable changes to this project will be documented in this file.

1.1.6 - 2015-05-09
    - Bugfix: Can't create more then 1 profile
    - Bugfix: Use find_executable instead of hardcoding the path to xrandr
    - Added: Add an exec_post hook when activating a profile

1.1.5 - 2014-09-09
    - Added: Implement the --dry-run option for the `create` subcommand.
    - Added: Improve verbose logging for the `auto` and `activate` subcommands
    - Added: unittest, code is now stable and has 97% coverage.
    - Added: Reduced the amount of xrandr calls needed (now always parsing
      xrandr --verbose). This should improve the `auto` and `create`
      subcommands.
    - Bugfix: `xprofile current` was not explicitly returning a 0 exit code
    - Bugfix: do not check or edid in the `create` subcommand
    - Bugfix: fix wrong usage of imported DEFAULT_SECTION variable
    - Removed: not setting DISPLAY=:0 anymore

1.1.4 - 2014-09-06
    - Added: man pages for xprofile(1) and xprofilerc(5)
    - Added: python 2.6 compatibility
    - Bugfix: do not continue executing if xrandr fails

1.1.3 - 2014-09-04
    - Added: This changelog file.

1.1.2 - 2014-09-04
    - Added: Make the project python 3.x compatible.

1.1.1 - 2014-09-04
    - Added: Include zsh completion in the pip package.

1.1.0 - 2014-09-04
    - Inital version.
