import pandas as pd
from lxml import etree
from collections import Counter


# -----------------------------
# Tag definitions
# -----------------------------

TAB_TAGS = ["tab"]
SECTION_TAGS = ["section"]
ROW_TAGS = ["row"]
COL_TAGS = ["col", "column"]


# -----------------------------
# Match tag helper
# -----------------------------

def tag_matches(tag, keywords):

    tag = tag.lower()

    return any(k in tag for k in keywords)


# -----------------------------
# Find nearest parent by tag
# -----------------------------

def find_parent(element, tag_list):

    parent = element.getparent()

    while parent is not None:

        if tag_matches(parent.tag, tag_list):
            return parent

        parent = parent.getparent()

    return None


# -----------------------------
# Extract text from
# <text><lang text="..."/></text>
# -----------------------------

def extract_display_text(node):

    if node is None:
        return None

    text_node = node.find("./text")

    if text_node is None:
        return None

    # case: text -> lang -> text attribute
    lang_node = text_node.find("./lang")

    if lang_node is not None:

        if lang_node.get("text"):
            return lang_node.get("text")

    # case: text attribute
    if text_node.get("text"):
        return text_node.get("text")

    # case: name attribute
    if text_node.get("name"):
        return text_node.get("name")

    # case: direct text value
    if text_node.text and text_node.text.strip():
        return text_node.text.strip()

    return None


# -----------------------------
# Get Tab Name
# -----------------------------

def get_tab_name(field):

    tab_node = find_parent(field, TAB_TAGS)

    name = extract_display_text(tab_node)

    if name:
        return name

    if tab_node is not None:
        return tab_node.tag

    return "UNKNOWN"


# -----------------------------
# Get Section Name
# -----------------------------

def get_section_name(field):

    section_node = find_parent(field, SECTION_TAGS)

    name = extract_display_text(section_node)

    if name:
        return name

    if section_node is not None:
        return section_node.tag

    return "UNKNOWN"


# -----------------------------
# Detect row node
# -----------------------------

def detect_row_node(field):

    return find_parent(field, ROW_TAGS)


# -----------------------------
# Detect column index
# -----------------------------

def detect_column(field, row_node):

    if row_node is None:
        return 1

    cols = row_node.findall(".//col")

    if not cols:
        return 1

    for i, col in enumerate(cols, start=1):

        if field in col.iter():
            return i

    return 1


# -----------------------------
# XML Structure Analyzer
# -----------------------------

def analyze_structure(file):

    tree = etree.parse(file)
    root = tree.getroot()

    tags = [elem.tag for elem in root.iter()]

    return dict(Counter(tags))


# -----------------------------
# Main XML Parser
# -----------------------------

def parse_xml(file):

    tree = etree.parse(file)
    root = tree.getroot()

    # detect fields via attribute
    fields = root.xpath(".//*[@fieldid]")

    if not fields:
        return pd.DataFrame()

    # collect all metadata attributes dynamically
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
