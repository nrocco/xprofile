# -*- coding: utf-8 -*-
import re
import codecs

from setuptools import setup
from setuptools.command.test import test as TestCommand


class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])


setup(
    name = 'xprofile',
    description = 'A tool to manage and automatically apply xrandr configurations.',
    version = re.search(r'''^__version__\s*=\s*["'](.*)["']''', open('xprofile/__init__.py').read(), re.M).group(1),
    author = 'Nico Di Rocco',
    author_email = 'dirocco.nico@gmail.com',
    url = 'https://github.com/nrocco/xprofile',
    license = 'GPLv3',
    long_description = codecs.open('README.rst', 'rb', 'utf-8').read(),
    test_suite='nose.collector',
    install_requires = [
        'docutils>=0.12'
    ],
    tests_require = [
        'nose',
        'mock',
        'coverage',
    ],
    packages = [
        'xprofile'
    ],
    entry_points = {
        'console_scripts': [
            'xprofile = xprofile.__main__:main'
        ]
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Desktop Environment',
        'Topic :: Utilities'
    ],
    cmdclass = {
        'test': NoseTestCommand
    }
)
