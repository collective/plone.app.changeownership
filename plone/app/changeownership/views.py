from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.changeownership import i18nMessageFactory as _
from plone.app.changeownership.utils import ChangeOwnerHandler
from plone.app.changeownership.utils import UserInfo
from zExceptions import Redirect
from zope.component import getMultiAdapter


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
