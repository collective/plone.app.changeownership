from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.changeownership import i18nMessageFactory as _
from plone.memoize.view import memoize
from zope.component import getMultiAdapter
import logging

logger = logging.getLogger('change_owner')


class ChangeOwner(BrowserView):

    template = ViewPageTemplateFile("changeowner.pt")

    need_newowner_message = _(u"You have to select a new owner.")
    objects_updated_message = _(u"Objects updated")

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def isa_FoundationMember(self):
        """Is the current object a 'Foundation member' ? """
        return self.context.Type() == 'Foundation member'

    def item_type(self):
        """Returns the type of the current item"""
        return self.context.Type()

    def current_owner(self):
        """Returns the owner of the current item"""
        return self.context.getOwner()

    def dry_run(self):
        """Do we have to do a dry run ? """
        return self.request.form.get('dry_run', True)

    def change_owner(self):
        """Main method"""
        new_owner = self.request.form.get('newowner', '')
        path = self.request.form.get('path', '')
        dryrun = self.request.form.get('dry_run', '')
        ret = ''

        self.status = []
        if 'submit' in self.request.form:
            if not new_owner:
                self.status.append(self.need_newowner_message)

            if self.status:
                return self.template()

            query = {'Type': 'Foundation member'}
            query['path'] = '/'.join(self.context.getPhysicalPath())

            count = 0
            for brain in self.catalog(**query):
                if not dryrun:
                    obj = brain.getObject()
                    self._change_ownership(obj, new_owner)
                    if base_hasattr(obj, 'reindexObject'):
                        # We don't want change the last modification date
                        old_modification_date = obj.ModificationDate()
                        obj.reindexObject()
                        obj.setModificationDate(old_modification_date)
                        obj.reindexObject(idxs=['modified'])
                else:
                    ret += "%s " % brain.getPath()

                count += 1

            self.status.append(self.objects_updated_message + " (%s)" % count)
            if ret:
                self.status.append(ret)

        return self.template()

    def _change_ownership(self, obj, new_owner):
        """Change object ownership
        """

        #1. Change object ownership
        acl_users = getattr(self.context, 'acl_users')
        user = acl_users.getUserById(new_owner)

        if user is None:
            user = self.membership.getMemberById(new_owner)
            if user is None:
                raise KeyError, 'Only retrievable users in this site can be made owners.'

        obj.changeOwnership(user)


        #2. Remove old authors if we was asked to and add the new_owner
        #   as primary author
        if hasattr(aq_base(obj), 'Creators'):
            creators = list(obj.Creators())
        else:
            # Probably a Dexterity content type
            creators = list(obj.listCreators())

        if new_owner in creators:
        # Don't add same creator twice, but move to front
            del creators[creators.index(new_owner)]

        obj.setCreators([new_owner] + creators)


        roles = list(obj.get_local_roles_for_userid(new_owner))
        if 'Owner' not in roles:
            roles.append('Owner')
            obj.manage_setLocalRoles(new_owner, roles)
