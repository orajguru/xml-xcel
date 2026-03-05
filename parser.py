import pandas as pd
from lxml import etree


def get_parent_attr(element, tag_name):
    parent = element.getparent()
    while parent is not None:
        if parent.tag.lower() == tag_name:
            return parent.get("name")
        parent = parent.getparent()
    return "UNKNOWN"


def parse_xml(file):

    tree = etree.parse(file)
    root = tree.getroot()

    # Detect elements that represent fields
    fields = root.xpath(".//*[@fieldid]")

    if not fields:
        return pd.DataFrame()

    # Detect ALL metadata attributes dynamically
    metadata_keys = set()

    for f in fields:
        for k in f.attrib.keys():
            metadata_keys.add(k)

    metadata_keys = sorted(list(metadata_keys))

    records = []

    section_row_map = {}

    for field in fields:

        tab_name = get_parent_attr(field, "tab")
        section_name = get_parent_attr(field, "section")

        # Detect row
        row_node = None
        parent = field.getparent()

        while parent is not None:
            if parent.tag.lower() == "row":
                row_node = parent
                break
            parent = parent.getparent()

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

            # Detect column position
            cols = row_node.findall(".//col")

            if cols:
                for i, col in enumerate(cols, start=1):
                    if field in col.iter():
                        col_id = i
                        break

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
