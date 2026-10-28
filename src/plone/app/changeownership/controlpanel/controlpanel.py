from Acquisition import aq_base
from plone import api
from plone.app.changeownership import _
from plone.app.changeownership.interfaces import IChangeOwnerSchema
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form.form import EditForm

SCHEMA_PREFIX = "plone.app.changeownership.changeowner"


class ChangeOwnershipControlPanel(AutoExtensibleForm, EditForm):

    schema = IChangeOwnerSchema
    schema_prefix = SCHEMA_PREFIX
    label = _("Change Ownership")
    ignoreContext = True

    need_oldowners_message = _("You have to select one or more from the old owners.")
    need_newowner_message = _("You have to select a new owner.")
    objects_updated_message = _("Objects updated")

    @button.buttonAndHandler(_("Apply"), name="apply")
    def handleApply(self, action):

        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        target = data["path"]
        old_owners = list(data["oldowners"])
        new_owner = next(iter(data["newowner"]))
        delete_old_creators = data["delete_old_creators"]
        delete_old_owners = data["delete_old_owners"]
        change_modification_date = data["change_modification_date"]
        dry_run = data["dry_run"]

        catalog = api.portal.get_tool("portal_catalog")

        # clean up
        old_owners = [c for c in old_owners if c != new_owner]

        query = {"Creator": old_owners}
        query["path"] = "/".join(target.getPhysicalPath())

        counter = 0
        touched_paths = []

        for brain in catalog(**query):

            if not dry_run:
                obj = brain.getObject()
                self._change_ownership(
                    obj, new_owner, old_owners, delete_old_owners, delete_old_creators
                )

                if change_modification_date is True:
                    obj.reindexObject()
                else:
                    # We don't want change the last modification date
                    old_modification_date = obj.ModificationDate()
                    obj.reindexObject()
                    obj.setModificationDate(old_modification_date)
                    obj.reindexObject(idxs=["modified"])
            else:
                touched_paths.append(brain.getPath())

            counter += 1

        if touched_paths:
            if dry_run:
                self.status = _("No action is performed in dry-run mode") + "<br/>"
            self.status += (
                self.objects_updated_message
                + f" ({counter})"
                + "<br />"
                + "<br />".join(touched_paths)
            )
            return

        self.status = self.objects_updated_message
        # self.status = self.noChangesMessage

    def _change_ownership(
        self, obj, new_owner, old_owners, delete_old_owners, delete_old_creators
    ):
        """Change object ownership"""

        # 1. Change object ownership
        acl_users = self.context.acl_users
        user = acl_users.getUserById(new_owner)

        membership = api.portal.get_tool("portal_membership")

        if user is None:
            user = membership.getMemberById(new_owner)
            if user is None:
                raise KeyError(
                    "Only retrievable users in this site can be made owners."
                )

        obj.changeOwnership(user)

        # 2. Remove old authors if we was asked to and add the new_owner
        #   as primary author
        if hasattr(aq_base(obj), "Creators"):
            creators = list(obj.Creators())
        else:
            # Probably a Dexterity content type
            creators = list(obj.listCreators())
        if delete_old_creators:
            creators = [c for c in creators if c not in old_owners]

        if new_owner in creators:
            # Don't add same creator twice, but move to front
            del creators[creators.index(new_owner)]

        obj.setCreators([new_owner] + creators)

        # 3. Remove the "owner role" from the old owners if we was asked to
        #   and add the new_owner as owner
        if delete_old_owners:
            # remove old owners
            owners = [o for o in obj.users_with_local_role("Owner") if o in old_owners]
            for owner in owners:
                roles = list(obj.get_local_roles_for_userid(owner))
                roles.remove("Owner")
                if roles:
                    obj.manage_setLocalRoles(owner, roles)
                else:
                    obj.manage_delLocalRoles([owner])

        roles = list(obj.get_local_roles_for_userid(new_owner))
        if "Owner" not in roles:
            roles.append("Owner")
            obj.manage_setLocalRoles(new_owner, roles)


ChangeOwnershipControlPanelView = wrap_form(
    ChangeOwnershipControlPanel, ControlPanelFormWrapper
)
