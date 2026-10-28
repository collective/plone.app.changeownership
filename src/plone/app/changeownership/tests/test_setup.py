from plone.app.changeownership import PACKAGE_NAME
from plone.app.changeownership.interfaces import IBrowserLayer
from plone.app.changeownership.testing import INTEGRATION_TESTING
from plone.base.interfaces import INonInstallable
from plone.base.utils import get_installer
from plone.browserlayer import utils
from Products.CMFCore.utils import getToolByName
from zope.component import getAllUtilitiesRegisteredFor

import unittest


class TestSetupInstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def not_installables(self) -> list:
        not_installable = []
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            gnip = getattr(util, "getNonInstallableProducts", None)
            if gnip is None:
                continue
            not_installable.extend(gnip())
        return not_installable

    def test_addon_installed(self):
        """Test if ukd.theme is installed."""
        self.installer = get_installer(self.layer["portal"], self.layer["request"])
        self.assertTrue(self.installer.is_product_installed(PACKAGE_NAME))

    def test_browserlayer(self):
        """Test that IBrowserLayer is registered."""
        browser_layers = utils.registered_layers()
        self.assertIn(IBrowserLayer, browser_layers)

    def test_latest_version(self):
        """Test latest version of default profile."""
        portal = self.layer["portal"]
        version = portal.portal_setup.getLastVersionForProfile(
            f"{PACKAGE_NAME}:default"
        )
        profile_last_version = version[0] if version else ""
        self.assertTrue(profile_last_version == "1000")

    def test_not_installable(self):
        """Test hidden upgrade profiles"""
        not_installables = self.not_installables()
        self.assertIn(f"{PACKAGE_NAME}.upgrades", not_installables)

    def test_controlpanel_is_registered(self):
        portal = self.layer["portal"]
        controlpanel = getToolByName(portal, "portal_controlpanel")
        action = controlpanel.getActionObject("Products/change_ownership")
        self.assertTrue(action is not None)
