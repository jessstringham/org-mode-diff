import collections

OrgTree = collections.namedtuple('OrgTree', [
    'orgheading',  # org heading
    'properties',  # dictionary of property name to value
    'text_content',  # string of text contents
    'subtrees',  # list of OrgTrees
    'scheduled',
    'deadline',
])

OrgHeading = collections.namedtuple('OrgHeading', [
    'star_count',  # int
    'title',  # string
    'priority',  # string
    'todo',  # string
    'tags',  # list of strings
])


DiffTuple = collections.namedtuple('DiffTuple', [
    'old',
    'new',
])


def getattrs_from_diff(diff_tuple, property, default=None):
    return DiffTuple(getattr(diff_tuple.old, property, default), getattr(diff_tuple.new, property, default))


DiffResult = collections.namedtuple('DiffResult', [
    'type',  # comment, removal, new
    'prefix',
    'string',
])
