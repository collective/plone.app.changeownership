from plone.app.changeownership.testing import INTEGRATION_TESTING
from zope.schema import ValidationError

import unittest


class TestConstraints(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_constraint_list_not_empty(self):
        from plone.app.changeownership.constraints import validateListLength

        with self.assertRaises(ValidationError):
            validateListLength(1)

        with self.assertRaises(ValidationError):
            validateListLength("")

        with self.assertRaises(ValidationError):
            validateListLength([])

        with self.assertRaises(ValidationError):
            validateListLength(set())

        self.assertTrue({1})
        self.assertTrue({1, 2})

        self.assertTrue([1])
        self.assertTrue([1, 2])
