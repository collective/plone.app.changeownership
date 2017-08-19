# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE as PLONE_FIXTURE
except pkg_resources.DistributionNotFound:
    from plone.app.testing import PLONE_FIXTURE


class ChangeOwnershipLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plone.app.changeownership
        self.loadZCML(package=plone.app.changeownership)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.changeownership:default')
        workflowTool = getToolByName(portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        acl_users = getToolByName(portal, 'acl_users')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])
        acl_users.userFolderAddUser('user', 'secret', ['Member', 'Contributor'], [])


OWNERSHIP_FIXTURE = ChangeOwnershipLayer()
OWNERSHIP_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(OWNERSHIP_FIXTURE, ),
                       name="ChangeOwnership:Integration")
OWNERSHIP_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(OWNERSHIP_FIXTURE, ),
                       name="ChangeOwnership:Functional")
