# Bank Statement Extractor

A Streamlit web application that extracts and analyzes transaction data from bank statements using Claude AI. The application processes PDF bank statements, extracts transaction details, and provides analysis features including data filtering and summary statistics.

## Features

- PDF bank statement processing and data extraction
- Transaction data filtering by type and date range
- Summary analysis with key financial metrics
- Export functionality to Excel
- Interactive data visualization
- Responsive web interface

## Requirements

- Python 3.7+
- Streamlit
- Anthropic API access
- PyMuPDF (fitz)
- pandas
- Pillow
- base64
- tempfile

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bank-statement-extractor
```

2. Install required packages:
```bash
pip install streamlit anthropic pandas PyMuPDF Pillow
```

3. Set up your environment variables:
   - Create a `.streamlit/secrets.toml` file in your project directory
   - Add your Anthropic API key:
     ```toml
     ANTHROPIC_API_KEY = "your-api-key-here"
     ```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Upload a bank statement PDF through the web interface

3. The application will:
   - Process the PDF using Claude AI
   - Extract transaction data
   - Display the data in an interactive table
   - Provide filtering options
   - Generate summary analysis
   - Allow export to Excel

## Data Processing

The application processes bank statements by:
1. Converting PDF pages to images
2. Using Claude AI to extract transaction details
3. Parsing the response into a structured format
4. Organizing data into a pandas DataFrame

## Features Details

### Data Preview Tab
- Filter transactions by type
- Set custom date ranges
- Export data to Excel
- Interactive data table with sorting capabilities

### Summary Analysis Tab
- Total income and expenses metrics
- Current balance calculation
- Transaction distribution visualization
- Interactive charts

## Security Notes

- PDF processing is done locally
- API communication is secured via Anthropic's API
- No data is stored permanently
- Temporary files are automatically cleaned up

## Limitations

- Currently supports specific bank statement format as defined in the prompt
- Requires PDF files to be readable and properly formatted
- Processing time depends on PDF size and complexity

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Add your chosen license here]

## Support

For support, please [add contact information or support guidelines]
