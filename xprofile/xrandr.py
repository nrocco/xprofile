# -*- coding: utf-8 -*-
import os
import logging

from re import compile
from hashlib import md5
from subprocess import Popen, PIPE


log = logging.getLogger(__name__)


RE_EDID = compile(r'^\s*([a-f0-9]{32})$')
RE_CONNECTED = compile(r'^(\w+) connected.*$')
RE_XRANDR_NOISE   = compile(r'^(Screen|\t|  |$)')
RE_XRANDR_DISPLAY = compile(r'^(?P<name>[^\s]+) (?P<status>disconnected|connected|unknown connection) ?(?P<primary>primary)? ?(?P<geometry>(?P<width>[0-9]+)x(?P<height>[0-9]+)\+(?P<x>[0-9]+)\+(?P<y>[0-9]+))? ?(\([0-9a-fx]+\))? ?(?P<rotation>normal|left|inverted|right)? \((?P<modes>.*)\)')
RE_XRANDR_SCREEN = compile(r'^Screen (?P<screen>[0-9]+): minimum (?P<minimum>[0-9]+ x [0-9]+), current (?P<current>[0-9]+ x [0-9]+), maximum (?P<maximum>[0-9]+ x [0-9]+)')


class Screen(dict):
    def __init__(self, *args, **kwargs):
        self['displays'] = []
        super(Screen, self).__init__(*args, **kwargs)

    def get_xrandr_options(self):
        '''
        Loop through all active displays and create an xrandr compatible
        option list.
        '''
        line = []
        for display in self['displays']:
            line += display.get_xrandr_options()
        return line

    def get_edid(self):
        '''
        Get a md5 hash of all EDID of all currently connected displays
        '''
        md5sum = md5()

        for display in self['displays']:
            for edid in display['edid']:
                md5sum.update(edid)

        return md5sum.hexdigest()


class Display(dict):
    def get_xrandr_options(self):
        if not self['connected']:
            return []

        line = ['--output', self['name']]

        if not self['active']:
            line += ['--off']

            return line

        if self['primary']:
            line += ['--primary']

        line += [
            '--mode', self['geometry']['dimension'],
            '--pos',  self['geometry']['offset']
        ]

        if self['rotation']:
            line += ['--rotate', self['rotation']]

        return line


class Xrandr(object):
    def __init__(self, xrandr_bin='/usr/bin/xrandr', display=None):
        self.xrandr_bin = xrandr_bin
        self.display = display

    def get_screen(self):
        screen  = Screen()

        for line in self.call_xrandr(['--verbose']):
            parts = RE_XRANDR_DISPLAY.match(line)
            if parts:
                display = Display()
                display['name'] = parts.group('name')
                display['status'] = parts.group('status')
                display['connected'] = parts.group('status') == 'connected'

                if parts.group('rotation') == 'normal':
                    display['rotation'] = None
                else:
                    display['rotation'] = parts.group('rotation')
                display['primary'] = parts.group('primary') == 'primary'
                display['edid'] = []

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
                screen['displays'].append(display)
                continue

            parts = RE_EDID.match(line)
            if parts:
                edid = line.strip().encode()
                screen['displays'][-1]['edid'].append(edid)
                #print('{0}: Found an edid line {1}'.format(screen['displays'][-1]['name'], edid))

        return screen

    def call_xrandr(self, args=[]):
        '''
        Make a call to the xrandr binary in a subprocess
        '''
        current_env = os.environ.copy()

        if self.display:
            current_env['DISPLAY'] = self.display

        process = Popen([self.xrandr_bin] + args, env=current_env,
                        stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        status = process.wait()

        if status != 0:
            message = 'xrandr error: {0}'.format(stderr)
            log.error(message)
            raise RuntimeError(message)

        return stdout.decode().split('\n')
