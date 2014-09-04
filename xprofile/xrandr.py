# -*- coding: utf-8 -*-

import os

from re import compile
from hashlib import md5
from subprocess import Popen, PIPE


XRANDR  = '/usr/bin/xrandr'  # TODO: make this configurable

RE_EDID = compile(r'^\s*([a-f0-9]{32})$')
RE_CONNECTED = compile(r'^(\w+) connected.*$')
RE_XRANDR_NOISE   = compile(r'^(Screen|\t|  |$)')
RE_XRANDR_DISPLAY = compile(r'^(?P<name>[^\s]+) (?P<status>disconnected|connected|unknown connection) ?(?P<primary>primary)? ?(?P<geometry>(?P<width>[0-9]+)x(?P<height>[0-9]+)\+(?P<x>[0-9]+)\+(?P<y>[0-9]+))? ?(?P<rotation>normal|left|inverted|right)? \((?P<modes>.*)\)')


def _get_current_edid():
    '''
    Get a md5 hash of all EDID of all currently connected screens
    '''
    output = _call_xrandr(['--verbose'])
    md5sum = md5()

    for line in output.split('\n'):
        if RE_EDID.match(line):
            md5sum.update(line.strip())
    return md5sum.hexdigest()


def _parse_xrandr_output():
    '''
    Parse every `display` line from xrandr output and ignore the rest
    '''
    output = _call_xrandr()
    displays = []

    for line in output.split('\n'):
        parts = RE_XRANDR_DISPLAY.match(line)

        if not parts:
            continue

        display = {}
        display['name'] = parts.group('name')
        display['status'] = parts.group('status')
        display['connected'] = parts.group('status') == 'connected'
        display['rotation'] = parts.group('rotation')
        display['primary'] = parts.group('primary') == 'primary'

        if parts.group('geometry'):
            display['geometry'] = {}

            # TODO: we should parse all modes per display instead of this hack
            if display['rotation'] == 'left':
                display['geometry']['dimension'] = '%sx%s' % (parts.group('height'), parts.group('width'))
            else:
                display['geometry']['dimension'] = '%sx%s' % (parts.group('width'), parts.group('height'))
            display['geometry']['offset'] = '%sx%s' % (parts.group('x'), parts.group('y'))
        else:
            display['geometry'] = None

        display['active'] = isinstance(display['geometry'], dict)

        displays.append(display)

    return displays


def _get_current_xrandr_config():
    '''
    Loop through all active displays and create an xrandr compatible
    option list.
    '''
    line = []
    for display in _parse_xrandr_output():
        if not display['connected']:
            continue

        line += ['--output', display['name']]

        if not display['active']:
            line += ['--off']
            continue

        if display['primary']:
            line += ['--primary']

        line += [
            '--mode', display['geometry']['dimension'],
            '--pos',  display['geometry']['offset']
        ]

        if display['rotation']:
            line += ['--rotate', display['rotation']]

    return line


def _call_xrandr(args=[], display=None):
    '''
    Make a call to the xrandr binary in a subprocess
    '''
    current_env = os.environ.copy()

    if display:
        current_env['DISPLAY'] = display

    current_env['DISPLAY'] = ':0'  # TODO: Hack remove this

    process = Popen([XRANDR] + args, env=current_env, stdout=PIPE)
    stdout, stderr = process.communicate()
    status = process.wait()

    if status != 0:
        print_err('xrandr non-zero exit code detected: {}'.format(status))

    return stdout
