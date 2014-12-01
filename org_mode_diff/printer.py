def output_org_header(org):
    header = "*" * org.star_count
    if org.todo is not None:
        header += " " + org.todo
    if org.priority is not None:
        header += " " + org.priority
    header += " " + org.title
    if org.tags:
        header += "\t:" + ":".join(org.tags) + ":"

    return header


def properties(org):
    property_box = ""
    data = ""

    for key, value in org.iteritems():
        if key == "SCHEDULED":
            data += "SCHEDULED: %s " % (value,)
        elif key == "DEADLINE":
            data += "DEADLINE: %s" % (value,)
        else:
            property_box += ":%s: %s\n" % (key, value)

    if property_box:
        if data:
            data += "\n"
        data += ":PROPERTIES:\n"
        data += property_box
        data += ":END:\n"

    return data


def output_org(org):
    if org.orgheading is not None:
        print output_org_header(org.orgheading)
    print properties(org.properties)

    for subtree in org.subtrees:
        output_org(subtree)
