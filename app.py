
import streamlit as st
import pandas as pd
import io
from parser import parse_xml

st.set_page_config(page_title="XML → Excel Metadata Extractor (Pro)", layout="wide")

st.title("XML → Excel Metadata Extractor (Production Version)")

st.write(
"""Upload an XML configuration file.  
The tool automatically:
- Detects fields anywhere in the XML
- Handles row / col / nested layouts
- Extracts ALL metadata attributes dynamically
- Reconstructs Tab / Section hierarchy
- Generates a downloadable Excel data dictionary
"""
)

uploaded_file = st.file_uploader("Upload XML File", type=["xml"])

if uploaded_file:

    df = parse_xml(uploaded_file)

    if df.empty:
        st.error("No fields detected in XML.")
    else:
        st.success(f"Parsed {len(df)} fields")

        st.subheader("Preview")
        st.dataframe(df, use_container_width=True)

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Fields")

        st.download_button(
            label="Download Excel",
            data=buffer.getvalue(),
            file_name="xml_field_dictionary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
