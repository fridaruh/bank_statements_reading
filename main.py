import streamlit as st
import pandas as pd
import anthropic
import tempfile
import os
import base64
import fitz  # PyMuPDF
from PIL import Image
import io

def convert_pdf_to_images(pdf_content):
    """Convert PDF to images using PyMuPDF"""
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)
    return images

# Initialize Anthropic client
def init_client():
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    client = anthropic.Client(api_key=api_key)
    return client


def extract_table_from_response(response):
    """Extract table data from Claude's response and convert to DataFrame"""
    lines = response.split('\n')
    table_data = []
    start_parsing = False

    for line in lines:
        if '|' in line:
            if 'Date' in line:  # Header row
                start_parsing = True
                continue
            if start_parsing and line.strip('|- '):
                row = [
                    cell.strip() for cell in line.split('|') if cell.strip()
                ]
                if len(row) == 4:
                    table_data.append(row)

    df = pd.DataFrame(table_data,
                      columns=['Date', 'Concept', 'Amount (MXN)', 'Type'])
    df['Amount (MXN)'] = df['Amount (MXN)'].str.replace(',', '').astype(float)

    return df


def process_pdf(pdf_content):
    """Process PDF content using Claude API"""
    client = init_client()

    images = convert_pdf_to_images(pdf_content)

    prompt = """
    I'll give you the full bank statement as images with the information, you will have to read from page 3 to the last-2, in this case from 3 to 6  (in this case: 8-2 = 6) to extract the information to give me back a table with the following information:

Date, Concept (only the text after the word "CONCEPTO") and Amount (MXN), Type.

Example, in the description: PAGO TRANSFERENCIA SPEI HORA 09:44:38
ENVIADO A AZTECA
A LA CUENTA 127180001128564631
AL CLIENTE ANDRES CAZAREZ DIAZ (1)
(1) DATO NO VERIFICADO POR ESTA INSTITUCION
CLAVE DE RASTREO 2024110140014BMOV0000476736050
REF 3903381
CONCEPTO RENTA DEPTO CHAPULTEPEC

you will give as Concept only: RENTA DEPTO CHAPULTEPEC

The name type that refers if is income or expense

Return the data ONLY in a table format with columns:
| Date | Concept | Amount (MXN) | Type |
"""

    # Convert images to base64
    base64_images = [base64.b64encode(img).decode() for img in images]

    # Create message content with images as base64
    content = [{"type": "text", "text": prompt}]
    for img_base64 in base64_images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img_base64
            }
        })

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0,
        system="You are a PDF bank statement analyzer.",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return message.content[0].text


def create_excel_download_link(df):
    """Generate a download link for the Excel file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False)
        with open(tmp.name, 'rb') as f:
            excel_data = f.read()
        os.unlink(tmp.name)  # Delete temporary file
        b64 = base64.b64encode(excel_data).decode()
        return f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'


def main():
    st.set_page_config(page_title="Bank Statement Extractor", layout="wide")

    st.title("Bank Statement Data Extractor")
    st.write("Upload your bank statement PDF to extract transaction data")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        pdf_content = uploaded_file.read()

        with st.spinner('Processing PDF...'):
            # Process PDF and get response
            response = process_pdf(pdf_content)

            # Extract table data and convert to DataFrame
            df = extract_table_from_response(response)

            # Create tabs for preview and analysis
            tab1, tab2 = st.tabs(["Data Preview", "Summary Analysis"])

            with tab1:
                st.subheader("Transaction Data Preview")

                # Add filters
                st.write("Filter Data:")
                col1, col2 = st.columns(2)

                with col1:
                    selected_types = st.multiselect(
                        "Filter by Type",
                        options=df['Type'].unique(),
                        default=df['Type'].unique())

                with col2:
                    date_range = st.date_input(
                        "Select Date Range",
                        value=(pd.to_datetime(df['Date'].min()),
                               pd.to_datetime(df['Date'].max())))

                # Apply filters
                mask = df['Type'].isin(selected_types)
                df_filtered = df[mask]

                # Display filtered data
                st.dataframe(df_filtered,
                             use_container_width=True,
                             column_config={
                                 "Amount (MXN)":
                                 st.column_config.NumberColumn("Amount (MXN)",
                                                               format="$%.2f")
                             })

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Preview Excel Format"):
                        st.write("Excel Preview:")
                        st.dataframe(df_filtered)

                with col2:
                    excel_link = create_excel_download_link(df_filtered)
                    st.markdown(
                        f'<a href="{excel_link}" download="bank_statement_data.xlsx">'
                        '<button style="background-color:#4CAF50; color:white; padding:10px; '
                        'border:none; border-radius:5px; cursor:pointer;">'
                        'Download Excel File</button></a>',
                        unsafe_allow_html=True)

            with tab2:
                st.subheader("Summary Analysis")

                # Calculate metrics
                total_income = df[df['Type'] == 'Income']['Amount (MXN)'].sum()
                total_expenses = df[df['Type'] ==
                                    'Expense']['Amount (MXN)'].sum()
                balance = total_income - total_expenses

                # Display metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"${total_income:,.2f}")
                col2.metric("Total Expenses", f"${total_expenses:,.2f}")
                col3.metric("Balance", f"${balance:,.2f}")

                # Add transaction type distribution
                st.subheader("Transaction Distribution")
                transaction_counts = df['Type'].value_counts()
                st.bar_chart(transaction_counts)


if __name__ == "__main__":
    main()
