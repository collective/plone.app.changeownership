# -*- coding: utf-8 -*-

from plone.app.changeownership import logger
from Products.CMFCore.utils import getToolByName


def migrateTo1000(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-plone.app.changeownership:default')
    logger.info("Migrated to version 0.5")
