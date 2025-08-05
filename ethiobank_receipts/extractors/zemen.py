import re
import pdfplumber
import requests
import tempfile
from typing import Dict


def extract_zemen_receipt_data_from_url(pdf_url: str) -> Dict[str, str]:
    """
    Download Zemen Bank PDF receipt and extract data.

    Args:
        pdf_url (str): URL to PDF.

    Returns:
        Dict[str, str]: Extracted data.
    """
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    return extract_zemen_receipt_data(tmp_path)


def extract_zemen_receipt_data(pdf_path: str) -> Dict[str, str]:
    """
    Extract structured data from Zemen Bank PDF receipt.

    Args:
        pdf_path (str): Local path to PDF.

    Returns:
        Dict[str, str]: Extracted fields.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    data = {}

    patterns = {
        "Invoice No": r'Invoice No\.?:\s*([0-9]+)',
        "Date": r'Date[:\s]+([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',
        "Payer Name": r'Payer name:\s*([A-Z\s]+)',
        "Payer Account No": r'Payer account no\.:\s*([\d\*()X]+)',
        "Recipient Name": r'Recipient name:\s*([A-Za-z\s\.]+)',
        "Recipient Account No": r'Recipient account no\.:\s*([\d\*]+)',
        "Reference No": r'Reference No:\s*([A-Z0-9]+)',
        "Transaction Status": r'Transaction status:\s*(\w+)',
        "Transaction Detail": r'Transaction Detail\s+([A-Za-z\s\-]+)\s+ETB',
        "Settled Amount": r'ATM CASH WITHDRAWAL ETB\s*([\d,]+\.\d{2})',
        "Service Charge": r'Service Charge ETB\s*([\d,]+\.\d{2})',
        "VAT": r'VAT 15% ETB\s*([\d,]+\.\d{2})',
        "Total Amount Paid": r'Total Amount Paid ETB\s*([\d,]+\.\d{2})',
        "Amount in Words": r'Total amount in word:\s*([A-Z\s\-]+CENT\(S\))',
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            data[key] = m.group(1).title() if "Word" in key else m.group(1)

    return data
