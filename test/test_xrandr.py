# -*- coding: utf-8 -*-
from mock import patch
from xprofile import xrandr


with open('test/multi_screen.txt', 'rb') as file:
    XRANDR_MULTI_SCREEN = file.read()

with open('test/laptop_screen.verbose.txt', 'rb') as file:
    XRANDR_LAPTOP_SCREEN_VERBOSE = file.read()

with open('test/docked.txt', 'rb') as file:
    XRANDR_DOCKED_SCREEN = file.read()


@patch('xprofile.xrandr.Popen')
def test_call_xrandr_failure(Popen):
    Popen.return_value.communicate.return_value = (None, 'An unknown error occurred.')
    Popen.return_value.wait.return_value = 1
    try:
        edid = xrandr._call_xrandr(['--verbose'])
    except RuntimeError as err:
        assert str(err) == 'xrandr error: An unknown error occurred.'
    else:
        assert False, 'Failed to raise RuntimeError'

    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--verbose']


@patch('xprofile.xrandr.Popen')
def test_parse_xrandr_output(Popen):
    Popen.return_value.communicate.return_value = (XRANDR_MULTI_SCREEN, None)
    Popen.return_value.wait.return_value = 0

    displays = xrandr._parse_xrandr_output()

    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr']
    assert len(displays) == 3

    assert displays[0]['name'] == 'VGA1'
    assert displays[0]['connected'] == True
    assert displays[0]['status'] == 'connected'
    assert displays[0]['geometry']['dimension'] == '1280x1024'
    assert displays[0]['geometry']['offset'] == '0x0'
    assert displays[0]['active'] == True
    assert displays[0]['rotation'] == None
    assert displays[0]['primary'] == False

    assert displays[1]['name'] == 'DVI1'
    assert displays[1]['connected'] == True
    assert displays[1]['status'] == 'connected'
    assert displays[1]['geometry']['dimension'] == '1280x1024'
    assert displays[1]['geometry']['offset'] == '1280x0'
    assert displays[1]['active'] == True
    assert displays[1]['rotation'] == None
    assert displays[1]['primary'] == False

    assert displays[2]['name'] == 'TV1'
    assert displays[2]['connected'] == False
    assert displays[2]['status'] == 'unknown connection'
    assert displays[2]['geometry'] == None

@patch('xprofile.xrandr.Popen')
def test_get_current_xrandr_config(Popen):
    Popen.return_value.communicate.return_value = (XRANDR_MULTI_SCREEN, None)
    Popen.return_value.wait.return_value = 0

    config = xrandr._get_current_xrandr_config()

    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr']

    assert config == [
        '--output', 'VGA1', '--mode', '1280x1024', '--pos', '0x0',
        '--output', 'DVI1', '--mode', '1280x1024', '--pos', '1280x0'
    ]


@patch('xprofile.xrandr.Popen')
def test_get_current_edid(Popen):
    Popen.return_value.communicate.return_value = (XRANDR_LAPTOP_SCREEN_VERBOSE, None)
    Popen.return_value.wait.return_value = 0

    current_edid = xrandr._get_current_edid()

    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr', '--verbose']

    assert current_edid == "cfdee1377d86e245f2d187082f7a504a"


@patch('xprofile.xrandr.Popen')
def test_parse_xrandr_output_docked(Popen):
    Popen.return_value.communicate.return_value = (XRANDR_DOCKED_SCREEN, None)
    Popen.return_value.wait.return_value = 0

    displays = xrandr._parse_xrandr_output()

    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr']
    assert len(displays) == 8

    for index in [0, 5, 6]:
        assert displays[index]['connected'] == True
        assert displays[index]['status'] == 'connected'

    for index in [1, 2, 3, 4, 7]:
        assert displays[index]['connected'] == False
        assert displays[index]['status'] == 'disconnected'

    assert displays[0]['name'] == 'LVDS1'
    assert displays[0]['geometry'] == None

    assert displays[5]['name'] == 'HDMI3'
    assert displays[5]['geometry']['dimension'] == '1920x1080'
    assert displays[5]['geometry']['offset'] == '1930x0'
    assert displays[5]['rotation'] == 'left'

    assert displays[6]['name'] == 'DP2'
    assert displays[6]['geometry']['dimension'] == '1920x1080'
    assert displays[6]['geometry']['offset'] == '0x500'


@patch('xprofile.xrandr.Popen')
def test_get_current_xrandr_config_docked(Popen):
    Popen.return_value.communicate.return_value = (XRANDR_DOCKED_SCREEN, None)
    Popen.return_value.wait.return_value = 0

    config = xrandr._get_current_xrandr_config()

    assert Popen.called
    assert Popen.call_args[0][0] == ['/usr/bin/xrandr']

    assert config == [
        '--output', 'LVDS1', '--off',
        '--output', 'HDMI3', '--mode', '1920x1080', '--pos', '1930x0', '--rotate', 'left',
        '--output', 'DP2',   '--primary', '--mode', '1920x1080', '--pos', '0x500'
    ]


@patch('xprofile.xrandr.Popen')
def test_call_xrandr_set_display(Popen):
    Popen.return_value.communicate.return_value = (XRANDR_MULTI_SCREEN, None)
    Popen.return_value.wait.return_value = 0

    xrandr._call_xrandr([], display=':1')

    assert Popen.called
    assert Popen.call_args[1]['env']['DISPLAY'] == ':1'
