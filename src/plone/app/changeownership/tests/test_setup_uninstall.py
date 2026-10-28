from plone.app.changeownership import PACKAGE_NAME
from plone.app.changeownership.interfaces import IBrowserLayer
from plone.app.changeownership.testing import INTEGRATION_TESTING
from plone.base.utils import get_installer
from plone.browserlayer import utils
from Products.CMFCore.utils import getToolByName

import unittest


class TestSetupUninstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Custom setup for tests."""
        super().setUp()
        self.installer = get_installer(self.layer["portal"], self.layer["request"])
        self.installer.uninstall_product(PACKAGE_NAME)

    def test_addon_uninstalled(self):
        """Test if plone.app.changeownership is uninstalled."""
        self.assertFalse(self.installer.is_product_installed(PACKAGE_NAME))

    def test_browserlayer_not_registered(self):
        """Test that IBrowserLayer is not registered."""
        browser_layers = utils.registered_layers()

        self.assertNotIn(IBrowserLayer, browser_layers)

    def test_controlpanel_is_removed(self):

        portal = self.layer["portal"]
        controlpanel = getToolByName(portal, "portal_controlpanel")
        action = controlpanel.getActionObject("Products/change_ownership")
        self.assertTrue(action is None)
