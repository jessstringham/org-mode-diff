import unittest

from org_mode_diff.diff import org_items_are_similar
from org_mode_diff.diff import pair_up_subtrees
from org_mode_diff.diff import struct_diff
from org_mode_diff.models import OrgTree
from org_mode_diff.models import OrgHeading
from org_mode_diff.models import DiffTuple
from org_mode_diff.models import DiffResult


def _make_mock_org_tree(title, todo, tags, text_content, subtrees):
    return OrgTree(
        OrgHeading(1, title, None, todo, tags),
        (),
        text_content,
        subtrees,
        None,
        None
    )


class TestOrgItemsAreSimilar(unittest.TestCase):

    def setUp(self):
        self.my_item = _make_mock_org_tree("testtitle", "TODO", [], "", [])

        self.similar_to_my_item = [
            _make_mock_org_tree("testtitle", "TODO", [], "", [1, 2, 3]),
            _make_mock_org_tree("testtitle", "DONE", [], "", []),
            _make_mock_org_tree("test title", "DONE", [], "", []),
        ]

        self.different_than_my_item = [
            _make_mock_org_tree("totally different title", "TODO", [], "", [])
        ]

    def test_similar_items(self):
        for similar_item in self.similar_to_my_item:
            self.assertTrue(org_items_are_similar(self.my_item, similar_item))

    def test_different_items(self):
        for different_item in self.different_than_my_item:
            self.assertFalse(
                org_items_are_similar(self.my_item, different_item))


class TestPairSimilarItems(unittest.TestCase):

    def setUp(self):
        self.item1 = _make_mock_org_tree("testtitle", "TODO", (), "", ())
        self.item2 = _make_mock_org_tree(
            "totally different title", "TODO", (), "", ())
        self.item3 = _make_mock_org_tree(
            "another title that is different", "TODO", (), "", ())

    def test_unchanged_list(self):
        first_set_of_items = (
            self.item1,
            self.item2,
        )

        second_set_of_items = (
            self.item1,
            self.item2,
        )

        expected = (
            DiffTuple(self.item1, self.item1),
            DiffTuple(self.item2, self.item2),
        )

        self.assertEquals(
            pair_up_subtrees(
                DiffTuple(first_set_of_items, second_set_of_items)),
            expected
        )

    def test_remove_item(self):
        first_set_of_items = (
            self.item1,
            self.item2,
        )

        second_set_of_items = (
            self.item1,
        )

        expected = (
            DiffTuple(self.item1, self.item1),
            DiffTuple(self.item2, None),
        )

        self.assertEquals(
            pair_up_subtrees(
                DiffTuple(first_set_of_items, second_set_of_items)),
            expected
        )

    def test_add_item(self):
        first_set_of_items = (
            self.item1,
        )

        second_set_of_items = (
            self.item1,
            self.item2,
        )

        expected = (
            DiffTuple(self.item1, self.item1),
            DiffTuple(None, self.item2),
        )

        self.assertEquals(
            pair_up_subtrees(
                DiffTuple(first_set_of_items, second_set_of_items)),
            expected
        )

    def test_add_item_between(self):
        first_set_of_items = (
            self.item1,
            self.item3,
        )

        second_set_of_items = (
            self.item1,
            self.item2,
            self.item3,
        )

        expected = (
            DiffTuple(self.item1, self.item1),
            DiffTuple(None, self.item2),
            DiffTuple(self.item3, self.item3),
        )

        self.assertEquals(
            pair_up_subtrees(
                DiffTuple(first_set_of_items, second_set_of_items)),
            expected
        )

    def test_remove_item_between(self):
        first_set_of_items = (
            self.item1,
            self.item2,
            self.item3,
        )

        second_set_of_items = (
            self.item1,
            self.item3,
        )

        expected = (
            DiffTuple(self.item1, self.item1),
            DiffTuple(self.item2, None),
            DiffTuple(self.item3, self.item3),
        )

        self.assertEquals(
            pair_up_subtrees(
                DiffTuple(first_set_of_items, second_set_of_items)),
            expected
        )

    def test_flip_items(self):
        first_set_of_items = (
            self.item1,
            self.item2,
        )

        second_set_of_items = (
            self.item2,
            self.item1,
        )

        result = pair_up_subtrees(
            DiffTuple(first_set_of_items, second_set_of_items))

        # I don't really care about order yet, just that we match up at least one pair, like
        # (1, None)
        # (2, 2)
        # (None, 1)
        # For now, just test that there are 3 pairs

        self.assertEquals(
            len(pair_up_subtrees(DiffTuple(first_set_of_items, second_set_of_items))), 3)

    def test_different_item(self):
        first_set_of_items = (
            self.item1,
            self.item2,
        )

        second_set_of_items = (
            self.item1,
            self.item3,
        )

        expected = (
            DiffTuple(self.item1, self.item1),
            DiffTuple(self.item2, None),
            DiffTuple(None, self.item3),
        )

        self.assertEquals(
            pair_up_subtrees(
                DiffTuple(first_set_of_items, second_set_of_items)),
            expected
        )

# TODO: more tests!
class TestStructDiff(unittest.TestCase):

    def setUp(self):
        self.old = OrgTree(
            orgheading=None,
            properties=(),
            text_content='New Top-level comments',
            subtrees=(
                OrgTree(
                    orgheading=OrgHeading(
                        star_count=1, title='Item1', priority=None, todo=None, tags=()),
                    properties=(),
                    text_content='',
                    subtrees=(
                        OrgTree(
                            orgheading=OrgHeading(
                                star_count=2, title='Item2', priority=None, todo=None, tags=()),
                            properties=(),
                            text_content='New text',
                            subtrees=(),
                            scheduled=None,
                            deadline=None
                        ),
                    ),
                    scheduled=None,
                    deadline=None
                ),
                OrgTree(
                    orgheading=OrgHeading(
                        star_count=1, title='Item3', priority=None, todo=None, tags=()),
                    properties=(),
                    text_content='',
                    subtrees=(),
                    scheduled=None,
                    deadline=None
                ),
            ),
            scheduled=None,
            deadline=None
        )

        self.new = OrgTree(
            orgheading=None,
            properties=(),
            text_content='Top-level comments',
            subtrees=(
                OrgTree(
                    orgheading=OrgHeading(
                        star_count=1, title='Item1', priority=None, todo=None, tags=()),
                    properties=(),
                    text_content='',
                    subtrees=(
                        OrgTree(
                            orgheading=OrgHeading(
                                star_count=2, title='New name', priority=None, todo=None, tags=()),
                            properties=(),
                            text_content='',
                            subtrees=(),
                            scheduled=None,
                            deadline=None
                        ),
                    ),
                    scheduled=None,
                    deadline=None
                ),
                OrgTree(
                    orgheading=OrgHeading(
                        star_count=1, title='Item', priority=None, todo=None, tags=()),
                    properties=(),
                    text_content='',
                    subtrees=(),
                    scheduled=None,
                    deadline=None
                ),
            ),
            scheduled=None,
            deadline=None
        )

    def test_struct_diff(self):
        diff = struct_diff(
            DiffTuple(self.old, self.new), False, supress_output=True)
        self.assertEquals(diff, [
            DiffResult(type='diff', prefix='',
                       string='--- old\n+++ new\n@@ -1 +1 @@\n-New Top-level comments\n+Top-level comments'),
            DiffResult(type='comment', prefix='[updated]', string='* Item1'),
            DiffResult(type='diff', prefix='-', string='** Item2'),
            DiffResult(type='diff', prefix='+', string='** New name'),
            DiffResult(type='comment', prefix='[updated]', string='* Item'),
            DiffResult(type='diff', prefix='-', string='Item3'),
            DiffResult(type='diff', prefix='+', string='Item'),
        ])

    def test_struct_diff_headers_only(self):
        diff = struct_diff(
            DiffTuple(self.old, self.new), True, supress_output=True)
        self.assertEquals(diff, [
            DiffResult(type='comment', prefix='[updated]', string='* Item1'),
            DiffResult(type='diff', prefix='-', string='** Item2'),
            DiffResult(type='diff', prefix='+', string='** New name'),
            DiffResult(type='comment', prefix='[updated]', string='* Item'),
            DiffResult(type='diff', prefix='-', string='Item3'),
            DiffResult(type='diff', prefix='+', string='Item'),
        ])


if __name__ == "__main__":
    unittest.main()
