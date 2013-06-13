from django.core.management import call_command
from django.test import TestCase
from django.conf import settings
from StringIO import StringIO
from mock import MagicMock
from .finders import BowerFinder
from . import shortcuts, conf
import os


class BowerInstallCase(TestCase):
    """Test case for bower_install management command"""

    def setUp(self):
        shortcuts.bower_install = MagicMock()
        self.apps = settings.BOWER_INSTALLED_APPS

    def test_install(self):
        """Test install bower packages"""
        call_command('bower_install')

        for num, install_call in enumerate(
            shortcuts.bower_install.call_args_list
        ):
            self.assertEqual(install_call[0][0], self.apps[num])


class BowerFinderCase(TestCase):
    """Test finding installed with bower files"""

    def setUp(self):
        try:
            os.mkdir(conf.COMPONENTS_ROOT)
        except OSError:
            pass
        shortcuts.bower_install('jquery')
        self.finder = BowerFinder()

    def test_find(self):
        """Test staticfinder find"""
        path = self.finder.find('jquery/jquery.min.js')
        self.assertEqual(path, os.path.join(
            conf.COMPONENTS_ROOT, 'components', 'jquery/jquery.min.js',
        ))

    def test_list(self):
        """Test staticfinder list"""
        result = self.finder.list([])
        matched = [
            part for part in result if part[0] == 'jquery/jquery.min.js'
        ]
        self.assertEqual(len(matched), 1)


class BowerFreezeCase(TestCase):
    """Case for bower freeze"""

    def setUp(self):
        try:
            os.mkdir(conf.COMPONENTS_ROOT)
        except OSError:
            pass
        shortcuts.bower_install('jquery')
        shortcuts.bower_install('backbone')
        shortcuts.bower_install('underscore')

    def test_freeze_shortcut(self):
        """Test freeze shortcut"""
        installed = [
            package.split('#')[0] for package in shortcuts.bower_freeze()
        ]
        self.assertItemsEqual(installed, ['backbone', 'jquery', 'underscore'])

    def test_management_command(self):
        """Test freeze management command"""
        stdout = StringIO()
        call_command('bower_freeze', stdout=stdout)
        stdout.seek(0)
        output = stdout.read()

        self.assertIn('BOWER_INSTALLED_APPS', output)
        self.assertIn('backbone', output)