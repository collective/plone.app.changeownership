"""Module where all interfaces, events and exceptions live."""

from plone.app.changeownership import _
from plone.app.changeownership.constraints import validateListLength
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IChangeOwnerSchema(Interface):

    path = RelationChoice(
        title=_("Target"),
        description=_("Please select a target."),
        vocabulary="plone.app.vocabularies.Catalog",
        required=True,
    )

    oldowners = schema.Set(
        title=_("The old owners:"),
        value_type=schema.Choice(
            vocabulary="plone.app.changeownership.Oldowners",
        ),
        required=True,
        constraint=validateListLength,
    )

    newowner = schema.Set(
        title=_("The new owner:"),
        value_type=schema.Choice(
            vocabulary="plone.app.changeownership.Newowners",
        ),
        required=True,
        constraint=validateListLength,
    )

    delete_old_creators = schema.Bool(
        title=_("Remove old owners from the creators list"),
        required=False,
        default=False,
    )

    delete_old_owners = schema.Bool(
        title=_("Remove the 'owner role' for the old owners"),
        required=False,
        default=False,
    )

    change_modification_date = schema.Bool(
        title=_("Change the modification date"),
        required=False,
        default=False,
    )

    dry_run = schema.Bool(
        title=_("Perform as Dry Run"),
        required=False,
        default=True,
    )
