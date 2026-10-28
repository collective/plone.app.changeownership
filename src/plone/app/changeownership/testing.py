from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import WSGI_SERVER_FIXTURE
from Products.CMFCore.utils import getToolByName


class ChangeOwnershipLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plone.app.changeownership

        self.loadZCML(package=plone.app.changeownership)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.changeownership:default")

        portal.portal_setup.setLastVersionForProfile(
            "plone.app.changeownership:default", "1000"
        )
        portal.portal_setup.upgradeProfile("plone.app.changeownership:default")

        workflowTool = getToolByName(portal, "portal_workflow")
        workflowTool.setDefaultChain("simple_publication_workflow")

        acl_users = getToolByName(portal, "acl_users")

        setRoles(
            portal,
            TEST_USER_ID,
            [
                "Member",
                "Manager",
            ],
        )
        acl_users.userFolderAddUser(
            "user",
            "secret",
            ["Member", "Contributor"],
            [],
        )


FIXTURE = ChangeOwnershipLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="ChangeOwnership:Integration",
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="ChangeOwnership:Functional",
)
