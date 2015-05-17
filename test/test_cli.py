# -*- coding: utf-8 -*-
from distutils.spawn import find_executable
from mock import patch
from os import remove
from unittest import TestCase
from xprofile.__main__ import main


class XprofileTestCase(TestCase):
    xrandr_bin = find_executable('xrandr')

    def setUp(self):
        patcher = patch('xprofile.xrandr.Popen')
        patcher2 = patch('xprofile.xrandr.Screen.get_edid')

        if 'addCleanup' in dir(self):
            self.addCleanup(patcher.stop)
            self.addCleanup(patcher2.stop)
        else:
            # This is needed for python 2.6, there is no addCleanup method
            self.tearDownPatcher = [patcher, patcher2]

        self.xrandr = patcher.start()
        self.edid = patcher2.start()

    def tearDown(self):
        if 'tearDownPatcher' in dir(self):
            for patcher in self.tearDownPatcher:
                patcher.stop()

    def set_xrandr_mock(self, xrandr_output, edid='mocked-edid-value'):
        with open(xrandr_output, 'rb') as file:
            xrandr_stdout = file.read()

        self.xrandr.return_value.communicate.return_value = (xrandr_stdout, None)
        self.xrandr.return_value.wait.return_value = 0

        if edid:
            self.edid.return_value = edid

    def test_list_profiles(self):
        self.set_xrandr_mock('test/docked.txt')
        retval = main(['--config', 'test/xprofilerc_both_example', 'list'])

        assert retval == 0
        assert self.xrandr.called
        assert self.xrandr.call_args[0][0] == [self.xrandr_bin, '--verbose']

    def test_no_config_file(self):
        self.set_xrandr_mock('test/docked.txt')
        retval = main(['--config', 'test/non_existing_xprofilerc', 'list'])
        remove('test/non_existing_xprofilerc')

        assert retval == 0
        assert not self.xrandr.called

    def test_list_profiles_empty(self):
        self.set_xrandr_mock('test/docked.txt')
        retval = main(['--config', 'test/xprofilerc_empty', 'list'])

        assert retval == 0
        assert not self.xrandr.called

    def test_current_profile(self):
        self.set_xrandr_mock('test/docked.txt', 'c2989146488f57fa9dc5f7efc263b0fd1')
        retval = main(['--config', 'test/xprofilerc_both_example', 'current'])

        assert retval == 0
        assert self.xrandr.called
        assert self.xrandr.call_args[0][0] == [self.xrandr_bin, '--verbose']

    def test_current_profile_does_not_exist(self):
        self.set_xrandr_mock('test/docked.txt', 'dkfjkdjfkdjfkdkfjd')
        retval = main(['--config', 'test/xprofilerc_both_example', 'current'])

        assert retval == 1
        assert self.xrandr.called
        assert self.xrandr.call_args[0][0] == [self.xrandr_bin, '--verbose']

    def test_generate_profile(self):
        self.set_xrandr_mock('test/docked.txt')
        retval = main(['--config', 'test/xprofilerc_both_example', 'generate'])

        assert retval == 0
        assert self.xrandr.called
        assert self.xrandr.call_args[0][0] == [self.xrandr_bin, '--verbose']

    def test_activate_profile_auto_select_and_existing(self):
        self.set_xrandr_mock('test/docked.txt', 'c2989146488f57fa9dc5f7efc263b0fd1')
        retval = main(['--config', 'test/xprofilerc_both_example', 'activate'])

        assert retval == 0
        assert self.xrandr.called
        assert self.xrandr.call_args[0][0] == [
            self.xrandr_bin,
            '--output', 'LVDS1', '--off',
            '--output', 'DP2', '--mode', '1920x1080', '--pos', '0x500', '--primary',
            '--output', 'HDMI3', '--mode', '1920x1080', '--rotate', 'left', '--pos', '1930x0'
        ]

    def test_activate_profile_auto_select_and_non_existing(self):
        self.set_xrandr_mock('test/docked.txt', 'non-existing-edid')
        retval = main(['--config', 'test/xprofilerc_both_example', 'activate'])

        assert retval == 0
        assert self.xrandr.called
        assert self.xrandr.call_args[0][0] == [self.xrandr_bin, '--auto']

    def test_activate_profile(self):
        pass

    def test_activate_profile_non_existing(self):
        self.set_xrandr_mock('test/docked.txt')
        retval = main(['--config', 'test/xprofilerc_both_example', 'activate', 'non-existing-profile'])

        assert retval == 1
        assert not self.xrandr.called

    def test_activate_profile_with_dry_run(self):
        self.set_xrandr_mock('test/docked.txt', 'c2989146488f57fa9dc5f7efc263b0fd1')
        retval = main(['--config', 'test/xprofilerc_both_example', 'activate', '--dry-run'])

        assert retval == 0
        assert self.xrandr.called
