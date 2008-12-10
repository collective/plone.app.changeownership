from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

from zope.component import getMultiAdapter
from plone.memoize.view import memoize

from plone.app.changeownership import MessageFactory as _


class ChangeOwner(BrowserView):
    
    template = ViewPageTemplateFile("changeowner.pt")
    
    need_oldowners_message = _(u"You have to select one or more from the old owners.") 
    need_newowner_message = _(u"You have to select a new owner.") 
    objects_updated_message = _(u"Objects updated") 
    
    
    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membership(self):
        return getToolByName(self.context, 'portal_membership')


    def exclude_members_folder(self):
        """Do we have to exclude the members folder ? """
        return self.request.form.get('exclude_members_folder', True)


    def delete_old_creators(self):
        """Do we have to delete old owners from the creators list ? """
        return self.request.form.get('delete_old_creators', False)


    def delete_old_owners(self):
        """Do we have to delete old owners from the owners role list ? """
        return self.request.form.get('delete_old_owners', False)


    def list_authors(self):
        """Returns a list of members that have created objects 
        """
        authors = []
         
        for creator in self.catalog.uniqueValuesFor('Creator'):
            info = self.membership.getMemberInfo(creator)
            if info and info['fullname']:
                authors.append(dict(id=creator, name=info['fullname']))
            else:         
                authors.append(dict(id=creator, name=creator))
                 
        return authors
        
                
    @memoize                     
    def list_members(self):
        """Returns the list of all plone members
        """
        members = []
        # plone members
        pas_search = getMultiAdapter((self.context, self.request), name=u'pas_search')
        users = list(pas_search.searchUsers())
        # + zope root members
        users = users + list(self.context.getPhysicalRoot().acl_users.searchUsers())
        
        for user in users:
            info = self.membership.getMemberInfo(user['userid'])
            if info and info['fullname']:
                members.append(dict(id=user['userid'], name=info['fullname']))
            else:         
                members.append(dict(id=user['userid'], name=user['userid']))
        
        return members


    def change_owner(self):
         
         old_owners = self.request.form.get('oldowners', [])
         new_owner  = self.request.form.get('newowner', '')

         self.status = []
         if 'submit' in self.request.form:    

             if isinstance(old_owners, str):
                 old_owners = [old_owners]
             
             if not new_owner:
                 self.status.append(self.need_newowner_message)

             if not old_owners:
                 self.status.append(self.need_oldowners_message)
             
             if self.status:
                 return self.template()   

             #clean up
             old_owners = [c for c in old_owners if c != new_owner]

             members_folder_path = '/'.join(self.membership.getMembersFolder().getPhysicalPath())               
             query = {'Creator': old_owners}
             count = 0
             for brain in self.catalog(**query): 
                 if self.exclude_members_folder() and \
                    brain.getPath().startswith(members_folder_path):
                     #we dont want to change ownership for the members folder
                     #and its contents
                     continue
                     
                 obj = brain.getObject()        
                 self._change_ownership(obj, new_owner, old_owners)                 
                 if base_hasattr(obj, 'reindexObject'):
                     obj.reindexObject()
                     
                 count += 1
                  
             self.status.append(self.objects_updated_message + " (%s)" % count)
                 
         return self.template()



    def _change_ownership(self, obj, new_owner, old_owners):
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
        creators = list(obj.Creators())
        if self.delete_old_creators():
            creators = [c for c in creators if c not in old_owners]
            
        if new_owner in creators:
        # Don't add same creator twice, but move to front
            del creators[creators.index(new_owner)]
                                                                    
        obj.setCreators([new_owner] + creators)


        #3. Remove the "owner role" from the old owners if we was asked to 
        #   and add the new_owner as owner
        if self.delete_old_owners():
            #remove old owners
            owners = [o for o in obj.users_with_local_role('Owner') if o in old_owners]
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


