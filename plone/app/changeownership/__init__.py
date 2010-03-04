from zope.i18nmessageid import MessageFactory

i18nMessageFactory = MessageFactory('plone.app.changeownership')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
