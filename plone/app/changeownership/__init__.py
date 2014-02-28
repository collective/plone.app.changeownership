# -*- coding: utf-8 -*-

import logging
from zope.i18nmessageid import MessageFactory

logger = logging.getLogger("plone.app.changeownership")
i18nMessageFactory = MessageFactory('plone.app.changeownership')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
