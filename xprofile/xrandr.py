# -*- coding: utf-8 -*-
import os
import logging

from re import compile
from hashlib import md5
from subprocess import Popen, PIPE
from distutils.spawn import find_executable


log = logging.getLogger(__name__)


RE_EDID = compile(r'^\s*([a-f0-9]{32})$')
RE_XRANDR_DISPLAY = compile(r'^(?P<name>[^\s]+) (?P<status>disconnected|connected|unknown connection) ?(?P<primary>primary)? ?(?P<geometry>(?P<width>[0-9]+)x(?P<height>[0-9]+)\+(?P<x>[0-9]+)\+(?P<y>[0-9]+))? ?(?P<mode>\([0-9a-fx]+\))? ?(?P<rotation>normal|left|inverted|right)?.*$')
RE_XRANDR_SCREEN = compile(r'^Screen (?P<screen>[0-9]+): minimum (?P<minimum>[0-9]+ x [0-9]+), current (?P<current>[0-9]+ x [0-9]+), maximum (?P<maximum>[0-9]+ x [0-9]+)')
RE_DISPLAY_MODE = compile(r'^\s+(?P<dimension>[0-9x]+) (?P<modeid>\([0-9a-fx]+\)) [0-9\.]+MHz [-+]HSync [-+]VSync ?(?P<current>\*current)? ?(?P<preferred>\+preferred)?\s*$')


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
    def __init__(self, *args, **kwargs):
        self['edid'] = []
        self['modes'] = {}
        self['geometry'] = None
        super(Display, self).__init__(*args, **kwargs)

    def get_xrandr_options(self):
        if not self['connected']:
            return []

        line = ['--output', self['name']]

        if not self['active']:
            line += ['--off']

            return line

        if self['primary']:
            line += ['--primary']

        if self['mode'] in self['modes']:
            mode = self['modes'][self['mode']]['dimension']
        else:
            # TODO: is this fallback needed?
            mode = self['geometry']['dimension']

        line += [
            '--mode', mode,
            '--pos',  self['geometry']['offset']
        ]

        if self['rotation']:
            line += ['--rotate', self['rotation']]

        return line


class Xrandr(object):
    def __init__(self, xrandr_bin=find_executable('xrandr'), display=None):
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
                display['primary'] = parts.group('primary') == 'primary'
                display['mode'] = parts.group('mode')

                if parts.group('rotation') == 'normal':
                    display['rotation'] = None
                else:
                    display['rotation'] = parts.group('rotation')

                if parts.group('geometry'):
                    display['geometry'] = {
                        'dimension': '%sx%s' % (parts.group('width'), parts.group('height')),
                        'offset':    '%sx%s' % (parts.group('x'), parts.group('y'))
                    }

                display['active'] = isinstance(display['geometry'], dict)
                screen['displays'].append(display)
                continue

            parts = RE_EDID.match(line)
            if parts:
                edid = line.strip().encode()
                screen['displays'][-1]['edid'].append(edid)
                continue

            parts = RE_DISPLAY_MODE.match(line)
            if parts:
                screen['displays'][-1]['modes'][parts.group('modeid')] = {
                    'id': parts.group('modeid'),
                    'dimension': parts.group('dimension'),
                    'current': parts.group('current') != None,
                    'preferred': parts.group('preferred') != None,
                }
                continue

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
