
import streamlit as st
import pandas as pd
import io
from parser import parse_xml, analyze_structure

st.set_page_config(page_title="XML Reverse Engineering Tool", layout="wide")

st.title("XML -> Excel")

st.write(
"""
Upload any XML UI/config file and the tool will:

• Detect fields dynamically  
• Identify tab / section / row hierarchy  
• Extract ALL metadata attributes  
• Generate a data dictionary Excel  
• Show XML structure insights  

"""
)

uploaded_file = st.file_uploader("Upload XML File", type=["xml"])

if uploaded_file:

    structure_info = analyze_structure(uploaded_file)

    st.subheader("XML Structure Overview")
    st.write(structure_info)

    uploaded_file.seek(0)

    df = parse_xml(uploaded_file)

    if df.empty:
        st.error("No fields with 'fieldid' attribute detected.")
    else:

        st.success(f"{len(df)} fields detected")

        st.subheader("Field Metadata Preview")
        st.dataframe(df, use_container_width=True)

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Fields")

        st.download_button(
            label="Download Data Dictionary (Excel)",
            data=buffer.getvalue(),
            file_name="xml_data_dictionary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
