# -*- coding: utf-8 -*-
import tempfile

from xprofile.__main__ import main

def test_create_new_profile():
    with tempfile.NamedTemporaryFile() as tmpfile:
        main(['--config', tmpfile.name, 'list'])
