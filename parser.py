
import pandas as pd
from lxml import etree
from collections import Counter


def analyze_structure(file):

    tree = etree.parse(file)
    root = tree.getroot()

    tags = [elem.tag for elem in root.iter()]

    tag_counts = Counter(tags)

    return dict(tag_counts)


def get_nearest_parent(element, tag_name):

    parent = element.getparent()

    while parent is not None:

        if parent.tag.lower() == tag_name:
            return parent.get("name")

        parent = parent.getparent()

    return "UNKNOWN"


def detect_row_node(element):

    parent = element.getparent()

    while parent is not None:

        if parent.tag.lower() == "row":
            return parent

        parent = parent.getparent()

    return None


def parse_xml(file):

    tree = etree.parse(file)
    root = tree.getroot()

    # detect field-like elements
    fields = root.xpath(".//*[@fieldid]")

    if not fields:
        return pd.DataFrame()

    # collect dynamic attributes
    attributes = set()

    for f in fields:
        attributes.update(f.attrib.keys())

    attributes = sorted(list(attributes))

    records = []

    section_row_map = {}

    for field in fields:

        tab = get_nearest_parent(field, "tab")
        section = get_nearest_parent(field, "section")

        row_node = detect_row_node(field)

        row_id = 1
        col_id = 1

        if row_node is not None:

            section_key = (tab, section)

            if section_key not in section_row_map:
                section_row_map[section_key] = {}

            row_map = section_row_map[section_key]

            if row_node not in row_map:
                row_map[row_node] = len(row_map) + 1

            row_id = row_map[row_node]

            cols = row_node.findall(".//col")

            if cols:

                for i, col in enumerate(cols, start=1):

                    if field in col.iter():
                        col_id = i
                        break

        record = {
            "Tab_Name": tab,
            "Section_Name": section,
            "Row_ID": row_id,
            "Column_ID": col_id
        }

        for attr in attributes:
            record[attr] = field.attrib.get(attr, "NULL")

        records.append(record)

    df = pd.DataFrame(records)

    return df
