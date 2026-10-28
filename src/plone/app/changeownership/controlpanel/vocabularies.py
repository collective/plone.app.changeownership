from plone import api
from plone.dexterity.interfaces import IDexterityContent
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class OldOwners:

    def __call__(self, context):

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            request = getRequest()
        else:
            request = context.REQUEST

        terms = []

        authors = []

        oldowners = request.form.get("oldowners", [])

        catalog = api.portal.get_tool("portal_catalog")

        membership = api.portal.get_tool("portal_membership")

        for creator in catalog.uniqueValuesFor("Creator"):

            if not creator:
                continue

            info = membership.getMemberInfo(creator)

            if info and info["fullname"]:
                d = {
                    "id": creator,
                    "name": f"{info.get('fullname', None)} ({creator})",
                }
            else:
                d = {
                    "id": creator,
                    "name": creator,
                }

            if creator in oldowners:
                d["selected"] = 1
            else:
                d["selected"] = 0

            authors.append(d)

        authors = sorted(authors, key=lambda x: str(x["name"]).lower())

        for item in authors:
            terms.append(
                SimpleTerm(
                    value=item.get("id"),
                    token=item.get("id"),
                    title=item.get("name"),
                )
            )

        return SimpleVocabulary(terms)


OldOwnerFactory = OldOwners()


@implementer(IVocabularyFactory)
class NewOwners:

    def __call__(self, context):

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            request = getRequest()
        else:
            request = context.REQUEST

        terms = []

        members = []

        pas_search = getMultiAdapter((context, request), name="pas_search")

        users = list(pas_search.searchUsers())

        users = users + list(context.getPhysicalRoot().acl_users.searchUsers())

        newowner = request.form.get("newowner", "")

        membership = api.portal.get_tool("portal_membership")

        for user in users:

            info = membership.getMemberInfo(user["userid"])

            if info and info["fullname"]:
                d = {
                    "id": user["userid"],
                    "name": f"{info.get('fullname', None)} ({user['userid']})",
                }
            else:
                d = {
                    "id": user["userid"],
                    "name": user["userid"],
                }
            if user["userid"] == newowner:
                d["selected"] = 1
            else:
                d["selected"] = 0
            members.append(d)

        members = sorted(members, key=lambda x: str(x["name"]).lower())

        for item in members:
            terms.append(
                SimpleTerm(
                    value=item.get("id"),
                    token=item.get("id"),
                    title=item.get("name"),
                )
            )

        return SimpleVocabulary(terms)


NewOwnerFactory = NewOwners()
