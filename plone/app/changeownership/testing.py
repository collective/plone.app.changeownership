# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig
from Products.CMFCore.utils import getToolByName

from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class ChangeOwnershipLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plone.app.changeownership
        xmlconfig.file('configure.zcml',
                       plone.app.changeownership,
                       context=configurationContext)
        z2.installProduct(app, 'plone.app.changeownership')

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
