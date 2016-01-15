from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.changeownership import i18nMessageFactory as _
from zope.component import getMultiAdapter


class ChangeOwnerHandler(object):
    objects_updated_message = _(u"Objects updated")

    def __init__(self, old_owners, new_owner, path, dry_run,
                 context, exclude_members_folder,
                 change_modification_date, delete_old_creators,
                 delete_old_owners):
        self.old_owners = old_owners
        self.new_owner = new_owner
        self.path = path
        self.dry_run = dry_run
        self.context = context
        self.exclude_members_folder = exclude_members_folder
        self.change_modification_date = change_modification_date
        self.delete_old_creators = delete_old_creators
        self.delete_old_owners = delete_old_owners

    def __call__(self):
        ret = []
        # clean up
        old_owners = [c for c in self.old_owners if c != self.new_owner]

        members_folder = self.membership_tool.getMembersFolder()
        members_folder_path = None
        if members_folder:
            members_folder_path = '/'.join(self.membership_tool
                                           .getMembersFolder()
                                           .getPhysicalPath())
        query = {'Creator': old_owners}
        if self.path:
            query['path'] = (self.context.portal_url
                             .getPortalObject().getId() + self.path)

        count = 0
        for brain in self.catalog(**query):
            if self.exclude_members_folder and members_folder_path and \
               brain.getPath().startswith(members_folder_path):
                # we dont want to change ownership for the members folder
                # and its contents
                continue

            if not self.dry_run:
                obj = brain.getObject()
                self._change_ownership(obj, self.new_owner, old_owners)
                if base_hasattr(obj, 'reindexObject'):
                    if self.change_modification_date:
                        obj.reindexObject()
                    else:
                        # We don't want change the last modification date
                        old_modification_date = obj.ModificationDate()
                        obj.reindexObject()
                        obj.setModificationDate(old_modification_date)
                        obj.reindexObject(idxs=['modified'])
            else:
                ret += "%s " % brain.getPath()

            count += 1

        ret.insert(0, self.objects_updated_message + " (%s)" % count)

        return ret

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membership_tool(self):
        return getToolByName(self.context, 'portal_membership')

    def _change_ownership(self, obj, new_owner, old_owners):
        """Change object ownership
        """

        # 1. Change object ownership
        acl_users = getattr(self.context, 'acl_users')
        user = acl_users.getUserById(new_owner)

        if user is None:
            user = self.membership_tool.getMemberById(new_owner)
            if user is None:
                raise KeyError('Only retrievable users in this site can be made owners.')  # NOQA

        obj.changeOwnership(user)

        # 2. Remove old authors if we was asked to and add the new_owner
        #   as primary author
        if hasattr(aq_base(obj), 'Creators'):
            creators = list(obj.Creators())
        else:
            # Probably a Dexterity content type
            creators = list(obj.listCreators())
        if self.delete_old_creators:
            creators = [c for c in creators if c not in old_owners]

        if new_owner in creators:
            # Don't add same creator twice, but move to front
            del creators[creators.index(new_owner)]

        obj.setCreators([new_owner] + creators)

        # 3. Remove the "owner role" from the old owners if we was asked to
        #    and add the new_owner as owner
        if self.delete_old_owners:
            # remove old owners
            owners = [o for o in obj.users_with_local_role('Owner')
                      if o in old_owners]
            for owner in owners:
                roles = list(obj.get_local_roles_for_userid(owner))
                roles.remove('Owner')
                if roles:
                    obj.manage_setLocalRoles(owner, roles)
                else:
                    obj.manage_delLocalRoles([owner])

        roles = list(obj.get_local_roles_for_userid(new_owner))
        if 'Owner' not in roles:
            roles.append('Owner')
            obj.manage_setLocalRoles(new_owner, roles)


class ChangeOwner(BrowserView):

    __call__ = ViewPageTemplateFile("changeowner.pt")

    need_oldowners_message = _(u"You have to select one or more from the old owners.")  # NOQA
    need_newowner_message = _(u"You have to select a new owner.")

    def __init__(self, context, request):
        super(ChangeOwner, self).__init__(context, request)
        f = self.request.form
        self.delete_old_owners = f.get('delete_old_owners', False)
        self.delete_old_creators = f.get('delete_old_creators', False)
        self.path = f.get('path', '')
        self.change_modification_date = f.get('change_modification_date',
                                              False)
        self.status = []

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membership(self):
        return getToolByName(self.context, 'portal_membership')

    def list_authors(self):
        """Returns a list of members that have created objects
        """
        authors = []
        oldowners = self.request.form.get('oldowners', [])

        for creator in self.catalog.uniqueValuesFor('Creator'):
            if not creator:
                continue

            info = self.membership.getMemberInfo(creator)
            if info and info['fullname']:
                d = dict(id=creator, name="%s (%s)" % (info['fullname'],
                                                       creator))
            else:
                d = dict(id=creator, name=creator)

            if creator in oldowners:
                d['selected'] = 1
            else:
                d['selected'] = 0
            authors.append(d)

        authors.sort(lambda a, b:
                     cmp(str(a['name']).lower(), str(b['name']).lower()))
        return authors

    def list_members(self):
        """Returns the list of all plone members
        """
        members = []
        newowner = self.request.form.get('newowner', '')

        # plone members
        pas_search = getMultiAdapter((self.context, self.request),
                                     name=u'pas_search')
        users = list(pas_search.searchUsers())
        # + zope root members
        users = users + list(self.context.getPhysicalRoot()
                             .acl_users.searchUsers())

        for user in users:
            info = self.membership.getMemberInfo(user['userid'])
            if info and info['fullname']:
                d = dict(id=user['userid'], name="%s (%s)" % (info['fullname'],
                                                              user['userid']))
            else:
                d = dict(id=user['userid'], name=user['userid'])
            if user['userid'] == newowner:
                d['selected'] = 1
            else:
                d['selected'] = 0
            members.append(d)

        members.sort(lambda a, b: cmp(str(a['name']).lower(),
                                      str(b['name']).lower()))
        return members

    def change_owner(self):
        """Main method"""
        f = self.request.form
        old_owners = f.get('oldowners', [])
        new_owner = f.get('newowner', '')
        self.dry_run = f.get('dry_run', False)
        self.exclude_members_folder = f.get('exclude_members_folder', False)

        if isinstance(old_owners, str):
            old_owners = [old_owners]

        if not new_owner:
            self.status.append(self.need_newowner_message)

        if not old_owners:
            self.status.append(self.need_oldowners_message)

        if self.status:
            return self.__call__()

        handler = ChangeOwnerHandler(old_owners, new_owner, self.path,
                                     self.dry_run,
                                     self.context,
                                     self.exclude_members_folder,
                                     self.change_modification_date,
                                     self.delete_old_creators,
                                     self.delete_old_owners)
        self.status.extend(handler())

        return self.__call__()
