# -*- coding: utf-8 -*-

from plone.app.changeownership import logger


def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-plone.app.changeownership:uninstall')
    logger.info("Uninstall done")


