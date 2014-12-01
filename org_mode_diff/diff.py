import difflib

import config
from helpers import smart_zip
from helpers import _sequence_similarity_ratio
from printer import output_org_header
from printer import output_org
from models import getattrs_from_diff
from models import DiffTuple
from models import DiffResult

def flatten_list_of_lists(lists):
    return sum(lists, [])


def print_diff(diff):
    for item in diff:
        print " ".join((item.prefix, str(item.string)))


def struct_diff(diff_tuple, headers_only, supress_output=False):
    """Compute the diff between two proceesd org files. Prints the diff of the result

    :param old: the previous org file
    :param new: the new org file

    :returns: None
    """

    diff = []

    if not headers_only:
        diff.append(
            diff_strings(getattrs_from_diff(diff_tuple, "text_content")))

    for subtree_diff_pair in pair_up_subtrees(getattrs_from_diff(diff_tuple, "subtrees")):
        diff.extend(diff_org_tree(subtree_diff_pair, headers_only))

    if not supress_output:
        print_diff(filter(None, diff))

    return diff


def simple_diff(diff_tuple):
    old, new = diff_tuple

    if old == new:
        return []

    if old is None:
        old = ""
    if new is None:
        new = ""

    return [
        DiffResult('diff', "-", old),
        DiffResult('diff', "+", new),
    ]


def diff_tuples_or_string(diff_tuple):
    old, new = diff_tuple

    if old == new:
        return []

    if new is None:
        return [DiffResult('diff', "-", old)]

    if old is None:
        return [DiffResult('diff', "+", new)]

    if isinstance(old, str) or isinstance(new, str):
        return simple_diff(diff_tuple)
    else:
        # If this is a nested structure, recurse
        return flatten_list_of_lists(
            diff_tuples_or_string(DiffTuple(o, n))
            for o, n
            in zip(old, new)
        )


def diff_strings(diff_tuple):
    old, new = diff_tuple

    if old != new:
        if old is None:
            old = ""
        if new is None:
            new = ""

        return DiffResult(
            'diff',
            '',
            '\n'.join(difflib.unified_diff(
                old.split('\n'),
                new.split('\n'),
                fromfile="old",
                tofile="new",
                lineterm="")))


def _simplify_org_tree(tree):
    """Simplifies a OrgTree to use when comparing."""
    # heuristic so we compare only the important bits
    # right now, we're just looking at the header
    org_heading_summary = tree.orgheading.title

    return org_heading_summary


def org_items_are_similar(old, new):
    """Determines if two OrgTrees are similar or not."""

    # Rather than comparing the entire tree and its subtrees, we just look at
    # a simplified version.
    simplified_old = _simplify_org_tree(old)
    simplified_new = _simplify_org_tree(new)

    # If they're identical, we're done here.
    if simplified_old == simplified_new:
        return True
    # If they're close enough, we're done here.
    if _sequence_similarity_ratio(simplified_old, simplified_new) > config.similarity_ratio_requirements:
        return True

    return False


def pair_up_subtrees(org_tree_list_diff_tuple):
    """Given two lists of OrgTrees, pairs them up"""
    return tuple(smart_zip(org_tree_list_diff_tuple, org_items_are_similar))


def diff_org_tree(org_tree_diff_tuple, headers_only):
    old = org_tree_diff_tuple.old
    new = org_tree_diff_tuple.new

    # either these items are the same...
    if old == new:
        return [DiffResult('comment', "#", output_org_header(new.orgheading))]
    # or one of them is new...
    if old is None:
        return [DiffResult('diff', "+", output_org_header(new.orgheading))]
    elif new is None:
        return [DiffResult('diff', "-", output_org_header(old.orgheading))]

    # or something more subtle has changed

    diff_results = [
        DiffResult('comment', "[updated]", output_org_header(new.orgheading))]

    diff_results.extend(diff_tuples_or_string(
        getattrs_from_diff(org_tree_diff_tuple, 'orgheading')))

    diff_results.extend(diff_properties(
        getattrs_from_diff(org_tree_diff_tuple, 'properties')))

    if not headers_only:
        diff_results.append(diff_strings(
            getattrs_from_diff(org_tree_diff_tuple, 'text_content')))

    schedule_info = diff_tuples_or_string(
        getattrs_from_diff(org_tree_diff_tuple, 'scheduled'))
    if schedule_info:
        diff_results.append(DiffResult('comment', "#", "scheduled"))
        diff_results.extend(schedule_info)

    deadline_info = diff_tuples_or_string(
        getattrs_from_diff(org_tree_diff_tuple, 'deadline'))
    if schedule_info:
        diff_results.append(DiffResult('comment', "#", "deadline"))
        diff_results.extend(deadline_info)

    for diff_tuple in pair_up_subtrees(getattrs_from_diff(org_tree_diff_tuple, 'subtrees')):
        diff_results.extend(diff_org_tree(diff_tuple, headers_only))

    return filter(None, diff_results)


def diff_properties(diff_tuple):
    def get_property_key(old, new):
        return old[0] == new[0]

    return flatten_list_of_lists(
        diff_tuples_or_string(property_diff_tuple)
        for property_diff_tuple
        in smart_zip(diff_tuple, similarity_function=get_property_key)
    )
