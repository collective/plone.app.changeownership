# -*- coding: utf-8 -*-

import unittest
from zope.component import getMultiAdapter
from DateTime import DateTime
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.changeownership.testing import OWNERSHIP_INTEGRATION_TESTING


class ChangeOWnershipTestCase(unittest.TestCase):

    layer = OWNERSHIP_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        self._createContent()

    def _createContent(self):
        portal = self.layer['portal']
        portal.invokeFactory(type_name="Document", id='page', title="New document")

    def test_fake_oldusers(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['oldowners'] = ['foo']
        request.form['newowner'] = 'user'
        request.form['submit'] = '1'
        request.method = 'POST'
        view = getMultiAdapter((portal.page, request), name=u"change-owner")
        view.change_owner()
        self.assertTrue(portal.page.Creator(), TEST_USER_ID)

    def test_fake_new_user(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['oldowners'] = [TEST_USER_ID]
        request.form['newowner'] = 'imnothere'
        request.form['submit'] = '1'
        request.method = 'POST'
        view = getMultiAdapter((portal.page, request), name=u"change-owner")
        self.assertRaises(KeyError, view.change_owner)

    def test_change_Creator(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['oldowners'] = [TEST_USER_ID]
        request.form['newowner'] = 'user'
        request.form['submit'] = '1'
        request.method = 'POST'
        view = getMultiAdapter((portal.page, request), name=u"change-owner")
        view.change_owner()
        self.assertEqual(portal.page.Creator(), 'user')

    def test_do_not_change_modification_time(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['oldowners'] = [TEST_USER_ID]
        request.form['newowner'] = 'user'
        request.form['change_modification_date'] = False
        request.form['submit'] = '1'
        request.method = 'POST'
        portal.page.setModificationDate(DateTime()-1)
        old_modification_date = portal.page.ModificationDate()
        view = getMultiAdapter((portal.page, request), name=u"change-owner")
        view.change_owner()
        self.assertEqual(portal.page.ModificationDate(), old_modification_date)
