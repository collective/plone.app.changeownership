from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bisect import insort
from functools import total_ordering
from plone.app.changeownership import i18nMessageFactory as _
from zExceptions import Redirect
from zope.component import getMultiAdapter


class ChangeOwnerHandler(object):
    objects_updated_message = _(u"Objects updated")

    def __init__(self,
                 context,
                 change_modification_date,
                 delete_old_creators,
                 delete_old_owners,
                 dry_run,
                 exclude_members_folder,
                 new_owner,
                 old_owners,
                 path):
        self.context = context

        self.change_modification_date = change_modification_date
        self.delete_old_creators = delete_old_creators
        self.delete_old_owners = delete_old_owners
        self.dry_run = dry_run
        self.exclude_members_folder = exclude_members_folder
        self.new_owner = new_owner
        self.old_owners = [c for c in old_owners if c != new_owner]
        self.path = path

    def __call__(self):
        ret = []
        members_folder = self.membership_tool.getMembersFolder()
        members_folder_path = None
        if members_folder:
            members_folder_path = '/'.join(self.membership_tool
                                           .getMembersFolder()
                                           .getPhysicalPath())

        count = -1

        for count, obj in enumerate(self._objectsToChange(
                members_folder_path)):
            if self.dry_run:
                ret.append(obj.absolute_url(relative=True))
                continue
            self._change_ownership(obj)
            if base_hasattr(obj, 'reindexObject'):
                if self.change_modification_date:
                    obj.reindexObject()
                else:
                    # We don't want change the last modification date
                    old_modification_date = obj.ModificationDate()
                    obj.reindexObject()
                    obj.setModificationDate(old_modification_date)
                    obj.reindexObject(idxs=['modified'])

        ret.insert(0, self.objects_updated_message + " (%s)" % count + 1)

        return ret

    def _objectsToChange(self, members_folder_path):
        query = {'Creator': self.old_owners}
        if self.path:
            query['path'] = (self.context.portal_url
                             .getPortalObject().getId() + self.path)
        for brain in self.catalog(**query):
            if self.exclude_members_folder and members_folder_path and \
               brain.getPath().startswith(members_folder_path):
                # we dont want to change ownership for the members folder
                # and its contents
                continue
            yield brain.getObject()

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membership_tool(self):
        return getToolByName(self.context, 'portal_membership')

    def _change_ownership(self, obj):
        """Change object ownership
        """

        # 1. Change object ownership
        acl_users = getattr(self.context, 'acl_users')
        user = acl_users.getUserById(self.new_owner)

        if user is None:
            user = self.membership_tool.getMemberById(self.new_owner)
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
            creators = [c for c in creators if c not in self.old_owners]

        if self.new_owner in creators:
            # Don't add same creator twice, but move to front
            del creators[creators.index(self.new_owner)]

        obj.setCreators([self.new_owner] + creators)

        # 3. Remove the "owner role" from the old owners if we was asked to
        #    and add the new_owner as owner
        if self.delete_old_owners:
            # remove old owners
            owners = [o for o in obj.users_with_local_role('Owner')
                      if o in self.old_owners]
            for owner in owners:
                roles = list(obj.get_local_roles_for_userid(owner))
                roles.remove('Owner')
                if roles:
                    obj.manage_setLocalRoles(owner, roles)
                else:
                    obj.manage_delLocalRoles([owner])

        roles = list(obj.get_local_roles_for_userid(self.new_owner))
        if 'Owner' not in roles:
            roles.append('Owner')
            obj.manage_setLocalRoles(self.new_owner, roles)


@total_ordering
class MemberData(dict):
    def __init__(self, userid, memberinfo):
        super(MemberData, self).__init__()
        self['id'] = userid
        if memberinfo and memberinfo['fullname']:
            self['name'] = '{} ({})'.format(memberinfo['fullname'],
                                            userid)
        else:
            self['name'] = userid

    def __eq__(self, other):
        if isinstance(other, MemberData):
            return str(self['name']).lower() == str(other['name']).lower()
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, MemberData):
            return str(self['name']).lower() < str(other['name']).lower()
        else:
            return NotImplemented


class UserInfo(object):

    def __init__(self, context, pas_search_tool):
        self.context = context
        self.pas_search_tool = pas_search_tool

    def _creators(self):
        return (getToolByName(self.context, 'portal_catalog')
                .uniqueValuesFor('Creator'))

    def _getMemberInfo(self, userid):
        return (getToolByName(self.context, 'portal_membership')
                .getMemberInfo(userid))

    def _getUserIds(self):
        # plone members
        for user in self.pas_search_tool.searchUsers():
            yield user['userid']
        # zope root members
        for user in (self.context.getPhysicalRoot()
                     .acl_users.searchUsers()):
            yield user['userid']

    def list_authors(self, preselected):
        """Returns a list of members that have created objects
        """
        authors = []

        for creator in self._creators():
            if not creator:
                continue
            memberinfo = self._getMemberInfo(creator)
            memberdata = MemberData(creator, memberinfo)
            memberdata['selected'] = memberdata['id'] in creator
            insort(authors, memberdata)

        return authors

    def list_members(self, preselected):
        """Returns the list of all plone members
        """
        members = []

        for user_id in self._getUserIds():
            memberinfo = self._getMemberInfo(user_id)
            memberdata = MemberData(user_id, memberinfo)
            memberdata['selected'] = memberdata['id'] is preselected
            insort(members, memberdata)

        return members


class ChangeOwner(BrowserView):

    template = ViewPageTemplateFile("changeowner.pt")

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
        self.old_owners = f.get('oldowners', [])
        if isinstance(self.old_owners, str):
            self.old_owners = [self.old_owners]
        self.new_owner = f.get('newowner', '')
        self.status = []

    def __call__(self):
        pas_search_tool = getMultiAdapter((self.context, self.request),
                                          name=u'pas_search')
        user_info = UserInfo(self.context, pas_search_tool)
        self.list_authors = user_info.list_authors(self.old_owners)
        self.list_members = user_info.list_members(self.new_owner)
        return self.template()

    def change_owner(self):
        """Main method"""
        if self.request.method != 'POST':
            raise Redirect(self.context.absolute_url() + '/change_owner')

        f = self.request.form
        # Sneaky workaround to have 3 different possibilities for bool in
        # the form: True, False, undefined == default
        self.dry_run = f.get('dry_run', False)
        self.exclude_members_folder = f.get('exclude_members_folder', False)

        if not self.new_owner:
            self.status.append(self.need_newowner_message)

        if not self.old_owners:
            self.status.append(self.need_oldowners_message)

        if self.status:
            return self.__call__()

        handler = ChangeOwnerHandler(self.context,
                                     self.change_modification_date,
                                     self.delete_old_creators,
                                     self.delete_old_owners,
                                     self.dry_run,
                                     self.exclude_members_folder,
                                     self.new_owner,
                                     self.old_owners,
                                     self.path)
        self.status.extend(handler())

        return self.__call__()
