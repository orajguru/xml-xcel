import pandas as pd
from lxml import etree
from collections import Counter


# -------------------------------
# Tag detection configuration
# -------------------------------

TAB_TAGS = ["tab", "tabpane", "tabpanel"]
SECTION_TAGS = ["section", "sectionpane", "group", "panel", "container", "block"]
ROW_TAGS = ["row"]
COL_TAGS = ["col", "column"]
LABEL_TAGS = ["text", "label", "title", "htag"]


# -------------------------------
# Utility: check tag contains keyword
# -------------------------------

def tag_matches(tag, keywords):
    tag = tag.lower()
    return any(k in tag for k in keywords)


# -------------------------------
# Extract display name from node
# -------------------------------

def extract_display_name(node):

    if node is None:
        return None

    # attribute priority
    for attr in ["name", "title", "label", "caption"]:
        if node.get(attr):
            return node.get(attr)

    # check label-like children
    for label_tag in LABEL_TAGS:

        child = node.find(f"./{label_tag}")

        if child is not None:

            if child.get("name"):
                return child.get("name")

            if child.text and child.text.strip():
                return child.text.strip()

    return None


# -------------------------------
# Find nearest parent by tag group
# -------------------------------

def find_parent(element, tag_list):

    parent = element.getparent()

    while parent is not None:

        if tag_matches(parent.tag, tag_list):
            return parent

        parent = parent.getparent()

    return None


# -------------------------------
# Extract tab name
# -------------------------------

def get_tab_name(field):

    tab_node = find_parent(field, TAB_TAGS)

    name = extract_display_name(tab_node)

    if name:
        return name

    if tab_node is not None and tab_node.get("id"):
        return tab_node.get("id")

    return "UNKNOWN"


# -------------------------------
# Extract section name
# -------------------------------

def get_section_name(field):

    section_node = find_parent(field, SECTION_TAGS)

    name = extract_display_name(section_node)

    if name:
        return name

    if section_node is not None and section_node.get("id"):
        return section_node.get("id")

    return "UNKNOWN"


# -------------------------------
# Detect row node
# -------------------------------

def detect_row_node(field):

    return find_parent(field, ROW_TAGS)


# -------------------------------
# Detect column position
# -------------------------------

def detect_column(field, row_node):

    if row_node is None:
        return 1

    cols = []

    for child in row_node.iter():
        if tag_matches(child.tag, COL_TAGS):
            cols.append(child)

    if not cols:
        return 1

    for i, col in enumerate(cols, start=1):

        if field in col.iter():
            return i

    return 1


# -------------------------------
# XML structure analysis
# -------------------------------

def analyze_structure(file):

    tree = etree.parse(file)
    root = tree.getroot()

    tags = [elem.tag for elem in root.iter()]

    return dict(Counter(tags))


# -------------------------------
# Main parser
# -------------------------------

def parse_xml(file):

    tree = etree.parse(file)
    root = tree.getroot()

    # detect fields by attribute instead of tag name
    fields = root.xpath(".//*[@fieldid]")

    if not fields:
        return pd.DataFrame()

    # collect dynamic metadata attributes
    metadata_keys = set()

    for f in fields:
        metadata_keys.update(f.attrib.keys())

    metadata_keys = sorted(list(metadata_keys))

    records = []

    section_row_map = {}

    for field in fields:

        tab_name = get_tab_name(field)
        section_name = get_section_name(field)

        row_node = detect_row_node(field)

        row_id = 1
        col_id = 1

        if row_node is not None:

            section_key = (tab_name, section_name)

            if section_key not in section_row_map:
                section_row_map[section_key] = {}

            row_map = section_row_map[section_key]

            if row_node not in row_map:
                row_map[row_node] = len(row_map) + 1

            row_id = row_map[row_node]

            col_id = detect_column(field, row_node)

        record = {
            "Tab_Name": tab_name,
            "Section_Name": section_name,
            "Row_ID": row_id,
            "Column_ID": col_id
        }

        for key in metadata_keys:
            record[key] = field.attrib.get(key, "NULL")

        records.append(record)

    df = pd.DataFrame(records)

    return df
