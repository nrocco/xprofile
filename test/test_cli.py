# -*- coding: utf-8 -*-
import tempfile

from mock import patch

from xprofile.xrandr import Xrandr
from xprofile.__main__ import main


@patch('xprofile.xrandr.Popen')
def test_create_new_profile(Popen):
    with open('test/docked.txt', 'rb') as file:
        xrandr_stdout = file.read()

    with tempfile.NamedTemporaryFile() as tmpfile:
        Popen.return_value.communicate.return_value = (xrandr_stdout, None)
        Popen.return_value.wait.return_value = 0

        retval = main(['--config', tmpfile.name, 'create', 'testprofile'])

        assert retval == 0
        assert Popen.called
        assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--verbose']


@patch('xprofile.xrandr.Popen')
def test_create_new_profile_dryrun(Popen):
    with open('test/docked.txt', 'rb') as file:
        xrandr_stdout = file.read()

    with tempfile.NamedTemporaryFile() as tmpfile:
        Popen.return_value.communicate.return_value = (xrandr_stdout, None)
        Popen.return_value.wait.return_value = 0

        retval = main(['--config', tmpfile.name, 'create', 'testprofile', '--dry-run'])

        assert retval == 0
        assert Popen.called
        assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--verbose']


@patch('xprofile.xrandr.Popen')
def test_create_existing_profile(Popen):
    with open('test/docked.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    retval = main(['--config', 'test/xprofilerc_example', 'create', 'laptop'])

    assert retval == 1
    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--verbose']

def test_list():
    main(['--config', 'test/xprofilerc_example', 'list'])


@patch('xprofile.xrandr.Popen')
def test_current(Popen):
    with open('test/docked.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    retval = main(['--config', 'test/xprofilerc_example', 'current'])

    assert retval == 0
    assert Popen.called


@patch('xprofile.xrandr.Popen')
def test_activate_profile(Popen):
    Popen.return_value.communicate.return_value = (b'', None)
    Popen.return_value.wait.return_value = 0

    retval = main(['--config', 'test/xprofilerc_example', 'activate', 'docked'])

    assert retval == 0
    assert Popen.called
    assert Popen.call_args[0][0] == [
        '/usr/bin/xrandr',
        '--output', 'LVDS1', '--off',
        '--output', 'DP2', '--mode', '1920x1080', '--pos', '0x500', '--primary',
        '--output', 'HDMI3', '--mode', '1920x1080', '--rotate', 'left', '--pos', '1930x0'
    ]


def test_activate_profile_nonexistent():
    retval = main(['--config', 'test/xprofilerc_example', 'activate', 'nonexistent'])

    assert retval == 1


@patch('xprofile.xrandr.Popen')
def test_activate_profile_auto(Popen):
    with open('test/laptop.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    retval = main(['--config', 'test/xprofilerc_example', 'auto'])

    assert retval == 0
    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--auto']


@patch('xprofile.xrandr.Popen')
def test_activate_profile_auto__dryrun(Popen):
    with open('test/laptop.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    retval = main(['--config', 'test/xprofilerc_example', 'auto', '--dry-run'])

    assert retval == 0
    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--verbose']


@patch('xprofile.xrandr.Popen')
def test_activate_profile_auto_nonexistent(Popen):
    with open('test/docked.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    retval = main(['--config', 'test/xprofilerc_example', 'auto'])

    assert retval == 0
    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--auto']
