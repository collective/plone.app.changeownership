from zope.i18nmessageid import MessageFactory

import logging

PACKAGE_NAME = "plone.app.changeownership"

logger = logging.getLogger(PACKAGE_NAME)

_ = MessageFactory(PACKAGE_NAME)
