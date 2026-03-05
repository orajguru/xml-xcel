
import pandas as pd
from lxml import etree

METADATA_COLUMNS = [
"req","fieldid","fieldtype","name","relatedtype","hidechar","resetonsave",
"searchable","hideformat","iseditable","listingtype","listingid","valign",
"showlabel","istileview","showlabelposition","maskingid","maskingtext",
"highlight","trackhist","hide","hidecontroltype","readonly","maxattachment",
"folderid","readonlytype","showtodropdown","renderingNameMode",
"requiredNameMode","salutationReq","suffixReq","isAutoComplete",
"isAutoSizeAlwd","controltype","rendering","evaluatorid","disableCopyPaste",
"searchop","isNewAlwd","colspan","rowspan","isuppercase"
]

def parse_xml(file):

    tree = etree.parse(file)
    root = tree.getroot()

    rows = []

    for tab in root.xpath(".//tab"):
        tab_name = tab.get("name")

        for section in tab.xpath(".//section"):
            section_name = section.get("name")

            row_counter = 1

            for row in section.xpath(".//row"):
                col_counter = 1

                for field in row.xpath(".//field"):
                    record = {
                        "Tab_Name": tab_name,
                        "Section_Name": section_name,
                        "Row_ID": row_counter,
                        "Column_ID": col_counter
                    }

                    for meta in METADATA_COLUMNS:
                        val = field.get(meta)
                        record[meta] = val if val is not None else "NULL"

                    rows.append(record)

                    col_counter += 1

                row_counter += 1

    df = pd.DataFrame(rows)
    return df
