import collections
import difflib
import functools

from models import DiffTuple


def score_zip(zip_result):
    return -len(zip_result)

# From https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer


@memoize
def smart_zip(diff_tuple, similarity_function=None):
    """Does a pairwise sequence alignment.

    diff_tuple -- diff_tuple containing iterables
    similarity_function -- function that determines if two items are similar. 
        Defaults to strict comparison

    returns a list of 2-tuples

    """
    if not similarity_function:
        similarity_function = lambda x, y: x == y

    old, new = diff_tuple

    if not new:
        return [DiffTuple(item, None) for item in old]
    if not old:
        return [DiffTuple(None, item) for item in new]

    old_item = old[0]
    new_item = new[0]

    if similarity_function(old_item, new_item):
        return [DiffTuple(old_item, new_item)] + smart_zip(DiffTuple(old[1:], new[1:]), similarity_function)
    else:
        skip_old = smart_zip(DiffTuple(old[1:], new), similarity_function)
        skip_new = smart_zip(DiffTuple(old, new[1:]), similarity_function)

        # use the one that found the most number of matches. If they're
        # equal, we lean towards keeping the old
        if score_zip(skip_new) > score_zip(skip_old):
            return [DiffTuple(None, new_item)] + skip_new
        else:
            return [DiffTuple(old_item, None)] + skip_old


def _sequence_similarity_ratio(simplified_old, simplified_new):
    """Returns a ratio that represents the similarity between the two strings."""
    sequence_match = difflib.SequenceMatcher(
        None, simplified_old, simplified_new)
    return sequence_match.ratio()
