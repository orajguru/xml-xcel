
# XML → Excel Field Extractor

Streamlit app that converts XML form definitions into an Excel sheet containing all fields and metadata.

## Features
- Upload XML
- Extract field metadata
- Capture Tab, Section, Row, Column hierarchy
- Export Excel
- Missing attributes filled as NULL

## Run Locally

pip install -r requirements.txt
streamlit run app.py

## Deploy on Streamlit Cloud

1. Upload this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Deploy new app
4. Select `app.py`
