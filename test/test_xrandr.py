# -*- coding: utf-8 -*-
from mock import patch
from xprofile.xrandr import Xrandr
from distutils.spawn import find_executable

xrandr_bin = find_executable('xrandr')

@patch('xprofile.xrandr.Popen')
def test_call_xrandr_failure(Popen):
    Popen.return_value.communicate.return_value = (None, 'An unknown error occurred.')
    Popen.return_value.wait.return_value = 1

    try:
        edid = Xrandr().get_screen()
    except RuntimeError as err:
        assert str(err) == 'xrandr error: An unknown error occurred.'
    else:
        assert False, 'Failed to raise RuntimeError'

    assert Popen.called
    assert Popen.call_args[0][0] == [xrandr_bin, '--verbose']


@patch('xprofile.xrandr.Popen')
def test_call_xrandr_set_display(Popen):
    Popen.return_value.communicate.return_value = (b'', None)
    Popen.return_value.wait.return_value = 0

    Xrandr(display=':1').call_xrandr()

    assert Popen.called
    assert Popen.call_args[1]['env']['DISPLAY'] == ':1'


@patch('xprofile.xrandr.Popen')
def test_xrandr_get_screen_multiple(Popen):
    with open('test/multi_screen.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    screen = Xrandr().get_screen()

    assert Popen.called
    assert Popen.call_args[0][0] == [xrandr_bin, '--verbose']
    assert len(screen['displays']) == 3

    assert screen['displays'][0]['name'] == 'VGA1'
    assert screen['displays'][0]['connected'] == True
    assert screen['displays'][0]['status'] == 'connected'
    assert screen['displays'][0]['geometry']['dimension'] == '1280x1024'
    assert screen['displays'][0]['geometry']['offset'] == '0x0'
    assert screen['displays'][0]['active'] == True
    assert screen['displays'][0]['rotation'] == None
    assert screen['displays'][0]['primary'] == False
    assert type(screen['displays'][0]['edid']) == list
    assert type(screen['displays'][0]['modes']) == dict

    assert screen['displays'][1]['name'] == 'DVI1'
    assert screen['displays'][1]['connected'] == True
    assert screen['displays'][1]['status'] == 'connected'
    assert screen['displays'][1]['geometry']['dimension'] == '1280x1024'
    assert screen['displays'][1]['geometry']['offset'] == '1280x0'
    assert screen['displays'][1]['active'] == True
    assert screen['displays'][1]['rotation'] == None
    assert screen['displays'][1]['primary'] == False
    assert type(screen['displays'][1]['edid']) == list
    assert type(screen['displays'][1]['modes']) == dict

    assert screen['displays'][2]['name'] == 'TV1'
    assert screen['displays'][2]['connected'] == False
    assert screen['displays'][2]['status'] == 'unknown connection'
    assert screen['displays'][2]['geometry'] == None
    assert type(screen['displays'][2]['edid']) == list
    assert type(screen['displays'][2]['modes']) == dict

    assert screen.get_xrandr_options() == [
        '--output', 'VGA1', '--mode', '1280x1024', '--pos', '0x0',
        '--output', 'DVI1', '--mode', '1280x1024', '--pos', '1280x0'
    ]

    assert screen.get_edid() == 'd41d8cd98f00b204e9800998ecf8427e'


@patch('xprofile.xrandr.Popen')
def test_xrandr_get_screen_docked(Popen):
    with open('test/docked.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    screen = Xrandr().get_screen()

    assert Popen.called
    assert Popen.call_args[0][0] == [xrandr_bin, '--verbose']
    assert len(screen['displays']) == 8

    for index in [0, 5, 6]:
        assert screen['displays'][index]['connected'] == True
        assert screen['displays'][index]['status'] == 'connected'
        assert type(screen['displays'][index]['edid']) == list
        assert type(screen['displays'][index]['modes']) == dict

    for index in [1, 2, 3, 4, 7]:
        assert screen['displays'][index]['connected'] == False
        assert screen['displays'][index]['status'] == 'disconnected'
        assert screen['displays'][index]['geometry'] == None
        assert screen['displays'][index]['primary'] == False
        assert screen['displays'][index]['active'] == False
        assert screen['displays'][index]['mode'] == None
        assert type(screen['displays'][index]['edid']) == list
        assert type(screen['displays'][index]['modes']) == dict

    assert screen['displays'][0]['name'] == 'LVDS1'
    assert screen['displays'][0]['geometry'] == None
    assert screen['displays'][0]['mode'] == None
    assert '(0x4b)' in screen['displays'][0]['modes']

    assert screen['displays'][5]['name'] == 'HDMI3'
    assert screen['displays'][5]['geometry']['dimension'] == '1080x1920'
    assert screen['displays'][5]['geometry']['offset'] == '1930x0'
    assert screen['displays'][5]['rotation'] == 'left'
    assert screen['displays'][5]['mode'] in screen['displays'][5]['modes']
    assert screen['displays'][5]['mode'] == '(0xc9)'
    assert screen['displays'][5]['modes']['(0xc9)']['current'] == True

    assert screen['displays'][6]['name'] == 'DP2'
    assert screen['displays'][6]['geometry']['dimension'] == '1920x1080'
    assert screen['displays'][6]['geometry']['offset'] == '0x500'

    assert screen.get_xrandr_options() == [
        '--output', 'LVDS1', '--off',
        '--output', 'HDMI3', '--mode', '1920x1080', '--pos', '1930x0', '--rotate', 'left',
        '--output', 'DP2',   '--primary', '--mode', '1920x1080', '--pos', '0x500'
    ]

    assert screen.get_edid() == 'c2989146488f57fa9dc5f7efc263b0fd'


@patch('xprofile.xrandr.Popen')
def test_xrandr_get_screen_laptop(Popen):
    with open('test/laptop.txt', 'rb') as file:
        xrandr_stdout = file.read()

    Popen.return_value.communicate.return_value = (xrandr_stdout, None)
    Popen.return_value.wait.return_value = 0

    screen = Xrandr().get_screen()

    assert Popen.called
    assert Popen.call_args[0][0] == [xrandr_bin, '--verbose']
    assert len(screen['displays']) == 8

    assert screen['displays'][0]['name'] == 'LVDS1'
    assert screen['displays'][0]['connected'] == True
    assert screen['displays'][0]['status'] == 'connected'
    assert screen['displays'][0]['mode'] == '(0x4b)'
    assert screen['displays'][0]['mode'] in screen['displays'][0]['modes']
    assert screen['displays'][0]['modes']['(0x4b)']['current'] == True
    assert screen['displays'][0]['geometry']['dimension'] == '1920x1080'
    assert screen['displays'][0]['geometry']['offset'] == '0x0'
    assert screen['displays'][0]['rotation'] == None

    assert type(screen['displays'][0]['edid']) == list
    assert type(screen['displays'][0]['modes']) == dict

    for display in screen['displays'][1:]:
        assert display['connected'] == False
        assert display['status'] == 'disconnected'
        assert display['geometry'] == None
        assert display['primary'] == False
        assert display['active'] == False
        assert display['mode'] == None
        assert type(display['edid']) == list
        assert type(display['modes']) == dict

    assert screen.get_xrandr_options() == [
        '--output', 'LVDS1', '--mode', '1920x1080', '--pos', '0x0'
    ]

    assert screen.get_edid() == 'cfdee1377d86e245f2d187082f7a504a'
