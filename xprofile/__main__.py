#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging

from argparse import ArgumentParser

from xprofile import __version__, DEFAULT_SECTION, xrandr


try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


log = logging.getLogger(__name__)


def list_all_profiles(args, config):
    '''
    List all known profiles from ~/.xprofilerc
    '''
    if len(config.sections()) > 0:
        print('\n'.join(config.sections()));

    return 0


def get_current_state(args, config):
    '''
    Print the current EDID to stdout
    Print the current xrandr configuration
    '''
    # TODO: detecting if profile active, or not
    print(xrandr._get_current_edid())
    print(' '.join(xrandr._get_current_xrandr_config()))


def activate_profile(args, config):
    '''
    Either activate the given profile, or if no profile is given
    automatically select a known profile by comparing the hashes of
    EDID's
    '''
    if not args.profile:
        current_edid = xrandr._get_current_edid()
        current_profile = None

        log.info('Auto detecting profile for EDID: %s', current_edid)

        for profile in config.sections():
            if config.get(profile, 'edid') == current_edid:
                current_profile = profile
                log.warn('Identified current state as profile: %s', profile)

        if not current_profile:
            current_profile = 'DEFAULT'
            log.error('No known profile found for EDID: %s', current_edid)

        xrandr_args = config.get(current_profile, 'args').split()

    elif not config.has_section(args.profile):
        log.error('Profile %s not found', args.profile)
        return 1

    else:
        xrandr_args = config.get(args.profile, 'args').split()
        log.info('Activating profile: %s', args.profile)

    log.info('Calling xrandr with: %s', ' '.join(xrandr_args))

    if not args.dry_run:
        xrandr._call_xrandr(xrandr_args)
    else:
        log.warn('Not calling xrandr because --dry-run option detected')

    return 0


def create_profile(args, config):
    '''
    Generate a new .ini style configuration section for the current EDID.
    '''
    current_edid = xrandr._get_current_edid()

    for profile in config.sections():
        if config.get(profile, 'edid') == current_edid:
            log.error('A profile `{0}` already exists for EDID `{1}`.'.format(profile, current_edid))
            return 1

    if not args.dry_run:
        config.add_section(args.profile)
        config.set(args.profile, 'name', args.description or '{0}\'s xrandr profile'.format(args.profile))
        config.set(args.profile, 'edid', current_edid)
        config.set(args.profile, 'args', ' '.join(xrandr._get_current_xrandr_config()))
        config.write(open(RCFILE, 'w'))
        print('Profile created in {0}'.format(RCFILE))
    else:
        print('blaat')

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

    parser_b = subparsers.add_parser('current', help="get information about the current state")
    parser_b.set_defaults(func=get_current_state)

    parser_c = subparsers.add_parser('auto', help="automatically select a known profile based on the current state")
    parser_c.add_argument('--dry-run', action='store_true', help='don\'t activate the profile')
    parser_c.set_defaults(func=activate_profile, profile=None)

    parser_d = subparsers.add_parser('activate', help="activate a known profile")
    parser_d.add_argument('--dry-run', action='store_true', help='don\'t activate the profile')
    parser_d.add_argument('profile', help='the profile to select')
    parser_d.set_defaults(func=activate_profile)

    parser_e = subparsers.add_parser('create', help="create a new profile based on the current state")
    parser_e.add_argument('--dry-run', action='store_true', help='don\'t write configuration to disk')
    parser_e.add_argument('--description', default=None, help='the description for the new profile')
    parser_e.add_argument('profile', help='the name for the new profile')
    parser_e.set_defaults(func=create_profile)

    return parser.parse_args(), parser


def main(args=None):
    '''
    Main entrypoint for this application
    '''
    # Parse command line arguments
    args, parser = parse_commandline_arguments(args)
    args.config = os.path.abspath(os.path.expanduser(args.config))

    # Setup logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARN,
                        format='%(message)s')

    # Create a configuration file if it does not exist
    if not os.path.exists(args.config):
        log.info('Creating config file because it does not exist: %s', args.config)
        with open(args.config, 'w') as file:
            file.write(xprofile.DEFAULT_SECTION.format(display=os.environ['DISPLAY']))

    # Read profile configuration
    config = ConfigParser()
    config.read(args.config)

    log.info('Read xrandr profile information from: %s', args.config)

    return args.func(args, config=config)


if '__main__' == __name__:
    sys.exit(main())
