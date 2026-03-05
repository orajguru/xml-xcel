
import streamlit as st
import pandas as pd
import io
from parser import parse_xml

st.set_page_config(page_title="XML → Excel Field Extractor", layout="wide")

st.title("XML → Excel Field Extractor")
st.write("Upload an XML file and download an Excel sheet with field metadata.")

uploaded_file = st.file_uploader("Upload XML file", type=["xml"])

if uploaded_file:
    st.success("XML uploaded successfully")

    df = parse_xml(uploaded_file)

    st.subheader("Preview")
    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Fields")

    st.download_button(
        label="Download Excel",
        data=buffer.getvalue(),
        file_name="xml_fields_dictionary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
