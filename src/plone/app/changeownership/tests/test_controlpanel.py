from plone.app.changeownership.testing import INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import unittest


class TestChangeOwnershipControlPanel(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_site_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="change-ownership-controlpanel"
        )
        self.assertTrue(view())

    def test_action_in_controlpanel(self):
        controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            "change_ownership"
            in [a.getAction(self.portal)["id"] for a in controlpanel.listActions()]
        )
