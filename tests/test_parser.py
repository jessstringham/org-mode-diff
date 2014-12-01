import unittest

from org_mode_diff import parser
from org_mode_diff.models import OrgHeading
from org_mode_diff.models import OrgTree


class TestParseHeaders(unittest.TestCase):

    def test_parse_header(self):
        self.assertEqual(
            parser.parse_org_header("* hello"),
            OrgHeading(
                star_count=1,
                title='hello',
                priority=None,
                todo=None,
                tags=tuple()))

    def test_parse_header_status(self):
        self.assertEqual(
            parser.parse_org_header("* TODO hello"),
            OrgHeading(
                star_count=1,
                title='hello',
                priority=None,
                todo='TODO',
                tags=tuple()))

    def test_parse_header_status_tag(self):
        self.assertEqual(
            parser.parse_org_header("* TODO hello   :blah:"),
            OrgHeading(
                star_count=1,
                title='hello',
                priority=None,
                todo='TODO',
                tags=('blah',)))

    def test_parse_header_status_tags(self):
        self.assertEqual(
            parser.parse_org_header("* TODO hello   :thing:blah:"),
            OrgHeading(
                star_count=1,
                title='hello',
                priority=None,
                todo='TODO',
                tags=('thing', 'blah')))

    def test_parse_header_tags(self):
        self.assertEqual(
            parser.parse_org_header("* hello   :thing:blah:"),
            OrgHeading(
                star_count=1,
                title='hello',
                priority=None,
                todo=None,
                tags=('thing', 'blah')))

    def test_parse_header_priority_tags(self):
        self.assertEqual(
            parser.parse_org_header("* [#A] hello   :thing:blah:"),
            OrgHeading(
                star_count=1,
                title='hello',
                priority='[#A]',
                todo=None,
                tags=('thing', 'blah')))

    def test_parse_header_priority(self):
        self.assertEqual(
            parser.parse_org_header("* [#A] hello "),
            OrgHeading(
                star_count=1,
                title='hello',
                priority='[#A]',
                todo=None,
                tags=tuple()))

    def test_parse_header_status_priority(self):
        self.assertEqual(
            parser.parse_org_header("* TODO [#A] hello "),
            OrgHeading(
                star_count=1,
                title='hello',
                priority='[#A]',
                todo='TODO',
                tags=tuple()))


class TestParser(unittest.TestCase):

    def test_no_items(self):
        lines = [
            "Top-level comments",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
                orgheading=None,
                properties=(),
                text_content='Top-level comments',
                subtrees=(),
                scheduled=None,
                deadline=None
            )
        )

    def test_single_header(self):
        lines = [
            "Top-level comments",
            "* SingleItem",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
                orgheading=None,
                properties=(),
                text_content='Top-level comments',
                subtrees=(
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='SingleItem', priority=None, todo=None, tags=()),
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
        )

    def test_multiple_headers(self):
        lines = [
            "Top-level comments",
            "* Item1",
            "* Item2",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
                orgheading=None,
                properties=(),
                text_content='Top-level comments',
                subtrees=(
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='Item1', priority=None, todo=None, tags=()),
                        properties=(),
                        text_content='',
                        subtrees=(),
                        scheduled=None,
                        deadline=None
                    ),
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='Item2', priority=None, todo=None, tags=()),
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
        )

    def test_single_header_with_content(self):
        lines = [
            "Top-level comments",
            "* SingleItem",
            "text",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
                orgheading=None,
                properties=(),
                text_content='Top-level comments',
                subtrees=(
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='SingleItem', priority=None, todo=None, tags=()),
                        properties=(),
                        text_content='text',
                        subtrees=(),
                        scheduled=None,
                        deadline=None
                    ),
                ),
                scheduled=None,
                deadline=None
            )
        )

    def test_single_header_with_content(self):
        lines = [
            "Top-level comments",
            "* SingleItem",
            "text",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
                orgheading=None,
                properties=(),
                text_content='Top-level comments',
                subtrees=(
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='SingleItem', priority=None, todo=None, tags=()),
                        properties=(),
                        text_content='text',
                        subtrees=(),
                        scheduled=None,
                        deadline=None
                    ),
                ),
                scheduled=None,
                deadline=None
            )
        )

    def test_multi_headers_with_content(self):
        lines = [
            "Top-level comments",
            "* Item1",
            "text",
            "* Item2",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
                orgheading=None,
                properties=(),
                text_content='Top-level comments',
                subtrees=(
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='Item1', priority=None, todo=None, tags=()),
                        properties=(),
                        text_content='text',
                        subtrees=(),
                        scheduled=None,
                        deadline=None
                    ),
                    OrgTree(
                        orgheading=OrgHeading(
                            star_count=1, title='Item2', priority=None, todo=None, tags=()),
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
        )

    def test_nested_headers(self):
        lines = [
            "Top-level comments",
            "* Item1",
            "** Item2",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
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
                                    star_count=2, title='Item2', priority=None, todo=None, tags=()),
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
                ),
                scheduled=None,
                deadline=None
            )
        )

    def test_exit_nested_headers(self):
        lines = [
            "Top-level comments",
            "* Item1",
            "** Item2",
            "* Item3",
        ]

        self.assertEqual(
            parser.parse_lines(lines),
            OrgTree(
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
                                    star_count=2, title='Item2', priority=None, todo=None, tags=()),
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
        )

if __name__ == '__main__':
    unittest.main()
