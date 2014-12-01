import re
from models import OrgHeading
from models import OrgTree
import config


class OrgParserException(Exception):
    pass


def first_word(string):
    return string.split()[0]


def rest_of_words(string):
    return ' '.join(string.split()[1:])


def parse_org_header(line):
    """Given a line, tries to parse it as a org header

    line -- string of a line from an org-mode file

    returns a OrgHeading
    """

    star_count = None
    priority = None
    todo = None
    title = None
    tags = []

    # First, we do a regex over it to get the easy stuff.
    # Group 1: stars (******)
    # Group 2: priority, todo, title
    # Group 3 (optional): tags (:blah:blahblah:)
    match = re.search("^(\*+)\s+(.*?)(?:\s+(\:(?:.*\:)*))?$", line)

    # If we don't find anything, this probably isn't an org heading
    if match is None:
        return None

    data = match.groups()

    if len(data) == 2:
        raw_stars, raw_maybe_priority_todo_title = data
        raw_tags = None
    elif len(data) == 3:
        raw_stars, raw_maybe_priority_todo_title, raw_tags = data

    # Parse stars
    star_count = len(raw_stars)

    # Priority, todo, and title
    # Now we try to pull out a status out of the string
    if first_word(raw_maybe_priority_todo_title) in config.status_values:
        todo = first_word(raw_maybe_priority_todo_title)
        raw_maybe_priority_todo_title = rest_of_words(
            raw_maybe_priority_todo_title)

    # and the same for priority
    if raw_maybe_priority_todo_title.startswith('[#'):
        priority = first_word(raw_maybe_priority_todo_title)
        raw_maybe_priority_todo_title = rest_of_words(
            raw_maybe_priority_todo_title)

    # whatever is left is the title
    title = raw_maybe_priority_todo_title

    # Tags
    if raw_tags is None:
        tags = tuple()
    else:
         # remove the first and last :, and split the rest into a list
        tags = tuple(raw_tags[1:-1].split(':'))

    return OrgHeading(
        star_count=star_count,
        title=title,
        priority=priority,
        todo=todo,
        tags=tags
    )


class OrgModeFileParser(object):

    """Parser than reads in a hierarchical org-mode document by consuming lines.

    Usage:
        parser = OrgModeFileParser()
        for line in org_file_lines:
            parser.consume(line)

        return parser.get_org_tree()


    org_header -- the org header for this section, or None if this is the top-level.
        If you are initalizing this, you will usually leave it blank.


    More details:
        At any given time, the OrgModeFileParser may have a child processor
    """

    def __init__(self, org_header=None):
        self.org_header = org_header
        self.depth = 0 if org_header is None else org_header.star_count

        self.content = ""
        self.subtrees = []
        self.properties = {}
        self.child_parser = None
        self.deadline = None
        self.scheduled = None

        self.is_reading_properties = False

    def _is_line_org_header(self, line):
        # kind of lame we need to do this twice
        return parse_org_header(line) is not None

    def _is_line_deadline_scheduled(self, line):
        return "DEADLINE:" in line or "SCHEDULE:" in line

    def _is_at_beginning_of_properties(self, line):
        return line.strip() == ":PROPERTIES:"

    def consume(self, line):
        """Consumes a line of an org-mode file. 
        Returns an org tree if we've reached the beginning of a new org tree, otherwise None.
        """

        # If we have a child parser, give it this line
        if self.child_parser is not None:
            process_response = self.child_parser.consume(line)

            # If we receive data, that means the child_parser has finished parsing its node.
            # We remove the child parser and go on to process the line ourself.
            # Otherwise, we're all done!
            if process_response is None:
                return
            else:
                self.child_parser = None
                self.subtrees.append(process_response)

        # Now it's time to read lines! Each line could be one of the following
        # * reading a org header
        # * reading a SCHEDULED and/or DEADLINE line
        # * at the beginning of a properties section
        # * in the middle of a properties section
        # * at the end of a properties section
        # * just another line, or one we don't support
        #
        # I use the self.is_reading_properties as a state, since properties are multi-line
        # (I could do something similar for logblocks!)
        # I don't support everthing org-mode has, so the rest should get thrown
        # in with content

        if self._is_line_org_header(line):
            org_header = parse_org_header(line)

            # If we're going down a level, start up a child parser to handle its content.
            # Otherwise, we've finished this node, so return the org tree
            if org_header.star_count - self.depth > 0:
                self.child_parser = OrgModeFileParser(org_header)
            else:
                return self.get_org_tree()

        elif self._is_line_deadline_scheduled(line):
            if "DEADLINE:" in line:
                match = re.search("DEADLINE: (<.*?>)", line)
                if match:
                    self.deadline = match.group(1)

            if "SCHEDULED:" in line:
                match = re.search("DEADLINE: (<.*?>)", line)
                if match:
                    self.scheduled = match.group(1)

        elif self._is_at_beginning_of_properties(line):
            self.is_reading_properties = True  # Now we're reading properties

        elif self.is_reading_properties:
            if ":END:" in line:
                self.is_reading_properties = False
            else:
                result = re.search(":(.*?):\s+(.*?)\s+$", line)
                if result:
                    key, value = result.groups()
                    self.properties[key] = value
                else:
                    raise OrgParserException(
                        ":PROPERTIES: missing :END:\n%s", line)
        else:
            self.content += line

    def get_org_tree(self):
        return OrgTree(
            orgheading=self.org_header,
            properties=tuple(self.properties.items()),
            text_content=self.content,
            subtrees=tuple(self.subtrees),
            deadline=self.deadline,
            scheduled=self.scheduled,
        )

    def flush(self):
        # First, we tell the child that it's over
        if self.child_parser is not None:
            self.subtrees.append(self.child_parser.flush())
        return self.get_org_tree()


def parse_lines(lines):
    parser = OrgModeFileParser()
    for line in lines:
        parser.consume(line)

    return parser.flush()
