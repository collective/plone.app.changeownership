# -*- coding: utf-8 -*-

import unittest

from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from plone.app.changeownership.testing import OWNERSHIP_INTEGRATION_TESTING


class ChangeOWnershipTestCase(unittest.TestCase):

    layer = OWNERSHIP_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

    def test_xxx(self):
        """Be sure that we have no problems with non-ASCII chars"""
        portal = self.layer['portal']
        request = self.layer['request']
