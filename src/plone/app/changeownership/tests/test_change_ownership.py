from DateTime import DateTime
from plone import api
from plone.app.changeownership.testing import FUNCTIONAL_TESTING
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser

import unittest


class TestBrowserFactory:

    def anonymous_browser(self):
        """Browser of anonymous"""
        import transaction

        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        return browser

    def manager_browser(self):
        """Browser with Manager authentication
        :return: Browser object with manager HTTP basic authentication header
        """
        return self._auth_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def member_browser(self):
        """Browser with Member authentication
        :return: Browser object with member HTTP basic authentication header
        """
        return self._auth_browser(TEST_USER_NAME, TEST_USER_PASSWORD)

    def user_browser(self, login, password):
        """Browser with Member authentication
        :return: Browser object with member HTTP basic authentication header
        """
        return self._auth_browser(login, password)

    def _auth_browser(self, login, password):
        """Browser of authenticated user
        :param login: A known user login
        :param password: The password for this user
        """
        browser = self.anonymous_browser()
        browser.addHeader("Authorization", f"Basic {login}:{password}")

        return browser


class ChangeOwnershipTestCase(unittest.TestCase, TestBrowserFactory):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer["portal"]

        # create users
        acl_users = portal.acl_users
        acl_users.userFolderAddUser("user1", "secret", ["Member"], [])
        acl_users.userFolderAddUser("user2", "secret", ["Member"], [])
        acl_users.userFolderAddUser("user3", "secret", ["Member"], [])

        login(portal, TEST_USER_NAME)

        # create content
        self.folder = api.content.create(
            type="Folder",
            title="a Folder",
            container=portal,
        )

        self.subfolder = api.content.create(
            type="Folder",
            title="a Folder",
            container=self.folder,
        )
        self.page = api.content.create(
            type="Document",
            title="a Page",
            container=self.subfolder,
        )

    def test_required_fields(self):

        portal = self.layer["portal"]
        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.buttons.apply").click()

        self.assertTrue("There were some errors" in browser.contents)

    def test_change_creator(self):

        portal = self.layer["portal"]

        self.assertTrue(self.page.Creator() == TEST_USER_ID)

        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.widgets.path").value = self.page.UID()
        browser.getControl(name="form.widgets.oldowners:list").value = [TEST_USER_ID]
        browser.getControl(name="form.widgets.newowner:list").value = ["user3"]
        browser.getControl(name="form.widgets.dry_run:list").value = False
        browser.getControl(name="form.buttons.apply").click()

        self.assertTrue("Objects updated" in browser.contents)
        self.assertTrue(self.page.Creator() == "user3")

    def test_change_creator_for_content_tree(self):

        portal = self.layer["portal"]

        self.assertTrue(self.folder.Creator() == TEST_USER_ID)
        self.assertTrue(self.subfolder.Creator() == TEST_USER_ID)
        self.assertTrue(self.page.Creator() == TEST_USER_ID)

        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.widgets.path").value = self.folder.UID()
        browser.getControl(name="form.widgets.oldowners:list").value = [TEST_USER_ID]
        browser.getControl(name="form.widgets.newowner:list").value = ["user2"]
        browser.getControl(name="form.widgets.dry_run:list").value = False
        browser.getControl(name="form.buttons.apply").click()

        self.assertTrue("Objects updated" in browser.contents)

        self.assertTrue(self.folder.Creator() == "user2")
        self.assertTrue(self.subfolder.Creator() == "user2")
        self.assertTrue(self.page.Creator() == "user2")

    def test_change_creator_dry_run(self):

        portal = self.layer["portal"]

        self.assertTrue(self.page.Creator() == TEST_USER_ID)

        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.widgets.path").value = self.page.UID()
        browser.getControl(name="form.widgets.oldowners:list").value = [TEST_USER_ID]
        browser.getControl(name="form.widgets.newowner:list").value = ["user3"]
        browser.getControl(name="form.widgets.dry_run:list").value = True
        browser.getControl(name="form.buttons.apply").click()

        self.assertTrue("Objects updated" in browser.contents)
        self.assertTrue(self.page.Creator() == TEST_USER_ID)

    def test_change_creator_for_content_tree_dry_run(self):

        portal = self.layer["portal"]

        self.assertTrue(self.folder.Creator() == TEST_USER_ID)
        self.assertTrue(self.subfolder.Creator() == TEST_USER_ID)
        self.assertTrue(self.page.Creator() == TEST_USER_ID)

        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.widgets.path").value = self.folder.UID()
        browser.getControl(name="form.widgets.oldowners:list").value = [TEST_USER_ID]
        browser.getControl(name="form.widgets.newowner:list").value = ["user2"]
        browser.getControl(name="form.widgets.dry_run:list").value = True
        browser.getControl(name="form.buttons.apply").click()

        self.assertTrue("Objects updated" in browser.contents)

        self.assertTrue(self.folder.Creator() == TEST_USER_ID)
        self.assertTrue(self.subfolder.Creator() == TEST_USER_ID)
        self.assertTrue(self.page.Creator() == TEST_USER_ID)

    def test_do_not_change_modification_time(self):

        portal = self.layer["portal"]

        self.folder.setModificationDate(DateTime() - 1)
        old_modification_date = self.folder.ModificationDate()

        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.widgets.path").value = self.folder.UID()
        browser.getControl(name="form.widgets.oldowners:list").value = [TEST_USER_ID]
        browser.getControl(name="form.widgets.newowner:list").value = ["user3"]
        browser.getControl(name="form.widgets.change_modification_date:list").value = (
            False
        )
        browser.getControl(name="form.widgets.dry_run:list").value = False
        browser.getControl(name="form.buttons.apply").click()

        self.assertEqual(self.folder.ModificationDate(), old_modification_date)

    def test_do_change_modification_time(self):

        portal = self.layer["portal"]

        self.folder.setModificationDate(DateTime() - 1)
        old_modification_date = self.folder.ModificationDate()

        browser = self.manager_browser()
        browser.open(portal.absolute_url() + "/change-ownership-controlpanel")
        browser.getControl(name="form.widgets.path").value = self.folder.UID()
        browser.getControl(name="form.widgets.oldowners:list").value = [TEST_USER_ID]
        browser.getControl(name="form.widgets.newowner:list").value = ["user3"]
        browser.getControl(name="form.widgets.change_modification_date:list").value = (
            True
        )
        browser.getControl(name="form.widgets.dry_run:list").value = False
        browser.getControl(name="form.buttons.apply").click()

        self.assertNotEqual(self.folder.ModificationDate(), old_modification_date)
