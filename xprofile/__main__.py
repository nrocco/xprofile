#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging

from argparse import ArgumentParser
from shlex import split
from subprocess import Popen

from xprofile import __version__, DEFAULT_SECTION
from xprofile.xrandr import Xrandr


try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


PROFILE_STRING = '''[{profile}]
name = {name}
edid = {edid}
args = {args}'''


log = logging.getLogger(__name__)

def _get_current_screen_and_edid():
    screen = Xrandr().get_screen()
    current_edid = screen.get_edid()

    log.debug('Edid of your current screen is: {0}'.format(current_edid))

    return (screen, current_edid)



def _get_profile_with_edid(edid, config):
    profile_name = None

    log.debug('Search through known profiles...')
    for profile in config.sections():
        if config.get(profile, 'edid') == edid:
            profile_name = profile
            break

    if not profile_name:
        log.debug('No known profile found with edid: {0}'.format(edid))
    else:
        log.debug('Known profile `{0}` found for edid: {1}'.format(profile_name, edid))

    return profile_name



def list_all_profiles(args, config):
    '''
    List all known profiles from ~/.xprofilerc

    The current profile is marked with a '*'
    '''
    known_profiles = config.sections()

    if len(known_profiles) == 0:
        log.warn('No profiles found')
        return 0

    screen, current_edid = _get_current_screen_and_edid()
    current_profile_name = _get_profile_with_edid(current_edid, config)
    padding = max([len(p) for p in known_profiles])

    for profile in known_profiles:
        vars = {
            'active': '*' if profile == current_profile_name else ' ',
            'name':    profile,
            'edid':    config.get(profile, 'edid'),
            'padding': padding
        }

        print('{active} {name:{padding}}\t{edid}'.format(**vars))

    return 0



def get_current_profile(args, config):
    '''
    Show the details of the current active profile
    '''
    screen, current_edid = _get_current_screen_and_edid()
    current_profile_name = _get_profile_with_edid(current_edid, config)

    if not current_profile_name:
        log.error('Currently no known profile is applied. '
                  'Use the `generate` subcommand to generate one.')
        return 1

    print(PROFILE_STRING.format(
        profile=current_profile_name,
        name=config.get(current_profile_name, 'name'),
        edid=config.get(current_profile_name, 'edid'),
        args=config.get(current_profile_name, 'args')
    ))

    return 0



def generate_profile(args, config):
    '''
    Generate configuration for the current EDID and print to stdout.
    '''
    screen, current_edid = _get_current_screen_and_edid()

    profile_name = args.profile or 'my-screen-setup'
    name = args.description or '{0}\'s xrandr profile'.format(profile_name)
    xrandr_args = ' '.join(screen.get_xrandr_options())

    print(PROFILE_STRING.format(profile=profile_name,
                                name=name,
                                edid=current_edid,
                                args=xrandr_args))
    return 0



def activate_profile(args, config):
    '''
    Either activate the given profile, or if no profile is given
    automatically select a known profile by comparing the hashes of
    EDID's
    '''
    xrandr = Xrandr()

    if not args.profile:
        screen, current_edid = _get_current_screen_and_edid()
        args.profile = _get_profile_with_edid(current_edid, config)

        if not args.profile:
            log.error('No known profile found, falling back to DEFAULT')
            args.profile = 'DEFAULT'

    elif not config.has_section(args.profile):
        log.error('No known profile found with name: {0}'.format(args.profile))
        return 1

    log.debug('Activating profile {0}...'.format(args.profile))
    xrandr_args = split(config.get(args.profile, 'args'))

    log.debug('Calling xrandr: {0}'.format(' '.join(xrandr_args)))

    if args.dry_run:
        log.warn('Not calling xrandr because --dry-run option detected')

        return 0

    xrandr.call_xrandr(xrandr_args)

    if config.has_option(args.profile, 'exec_post'):
        exec_post = config.get(args.profile, 'exec_post')

        log.debug('Calling exec_post: {0}'.format(exec_post))
        proc = Popen(split(exec_post), stdout=sys.stdout, stderr=sys.stderr)
        proc.communicate()

    return 0



def parse_commandline_arguments(args=None):
    '''
    Add several subcommands, each with their own options and arguments.
    '''
    parser = ArgumentParser(prog='xprofile', description='A tool to manage and automatically apply xrandr configurations.')

    parser.add_argument('--verbose', action='store_true', help='output more verbosely')
    parser.add_argument('--config',  default='~/.xprofilerc', help='config file to read profiles from')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    subparsers = parser.add_subparsers(description='The following commands are available', dest='subcommand')
    subparsers.required = True

    parser_a = subparsers.add_parser('list', help="list all available xrandr profiles")
    parser_a.set_defaults(func=list_all_profiles)

    parser_b = subparsers.add_parser('current', help="get information about the current active profile")
    parser_b.set_defaults(func=get_current_profile)

    parser_c = subparsers.add_parser('generate', help="generate a new profile and print to stdout")
    parser_c.add_argument('--description', default=None, help='the description for the new profile')
    parser_c.add_argument('--profile', default=None, help='the name for the new profile')
    parser_c.set_defaults(func=generate_profile)

    parser_d = subparsers.add_parser('activate', help="activate the given profile or automatically select one")
    parser_d.add_argument('--dry-run', action='store_true', help='don\'t activate the profile')
    parser_d.add_argument('profile', default=None, nargs='?', help='the profile to select')
    parser_d.set_defaults(func=activate_profile)

    if args:
        parsed_args = parser.parse_args(args)
    else:
        parsed_args = parser.parse_args()

    return parsed_args, parser



def main(args=None):
    '''
    Main entrypoint for this application
    '''
    # Parse command line arguments
    args, parser = parse_commandline_arguments(args)
    args.config = os.path.abspath(os.path.expanduser(args.config))

    # Setup logging
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(levelname)s: %(message)s')

    # Create a configuration file if it does not exist
    if not os.path.exists(args.config):
        log.warn('Creating config file because it does not exist: {0}'.format(args.config))
        with open(args.config, 'w') as file:
            file.write(DEFAULT_SECTION.format(display=os.environ['DISPLAY']))

    # Read profile configuration
    config = ConfigParser()
    config.read(args.config)

    log.debug('Read xrandr profile information from: {0}'.format(args.config))
    log.debug('Found {0} known profiles: {1}'.format(len(config.sections()),
                                                   config.sections()))
    return args.func(args, config=config)



if '__main__' == __name__:
    sys.exit(main())
