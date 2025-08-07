import re
from datetime import datetime
import pdfplumber
from concurrent.futures import ThreadPoolExecutor
from ethiobank_receipts.download import download_pdf_from_url


def extract_zemen_receipt_data(url):
    """Optimized Zemen Bank receipt extraction for PDFs similar to Dashen"""
    try:
        # Download PDF with connection pooling
        pdf_path = download_pdf_from_url(url)

        # Parallel text extraction from PDF pages
        def extract_page_text(page):
            text = page.extract_text()
            return text if text else ""

        with pdfplumber.open(pdf_path) as pdf:
            with ThreadPoolExecutor() as executor:
                page_texts = list(executor.map(extract_page_text, pdf.pages))
            full_text = " ".join(page_texts).replace("\n", " ")

        # Precompiled regex patterns for Zemen's specific format
            patterns = {
                'Invoice No': re.compile(r'Invoice No\.?:\s*(\d+)'),
                'Date': re.compile(r'Date[:\s]+([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})'),
                'Payer Name': re.compile(r'Payer name:\s*([A-Z\s]+)'),
                'Payer Account No': re.compile(r'Payer account no\.?:\s*([\d\*()X]+)'),
                'Recipient Name': re.compile(r'Recipient name:\s*([A-Za-z\s\.]+)'),
                'Recipient Account No': re.compile(r'Recipient account no\.?:\s*([\d\*]+)'),
                'Reference No': re.compile(r'Reference No:\s*([A-Z0-9]+)'),
                'Transaction Status': re.compile(r'Transaction status:\s*(\w+)'),
                'Transaction Detail': re.compile(r'Transaction Detail\s+([A-Za-z\s\-]+)\s+ETB'),
                'Settled Amount': re.compile(r'ATM CASH WITHDRAWAL ETB\s*([\d,]+\.\d{2})'),
                'Service Charge': re.compile(r'Service Charge ETB\s*([\d,]+\.\d{2})'),
                'VAT': re.compile(r'VAT 15% ETB\s*([\d,]+\.\d{2})'),
                'Total Amount Paid': re.compile(r'Total Amount Paid ETB\s*([\d,]+\.\d{2})'),
                'Amount in Words': re.compile(r'Total amount in word:\s*([A-Z\s\-]+CENT\(S\))')
            }

        # Extract all matching data
        result = {}
        for field, pattern in patterns.items():
            match = pattern.search(full_text)
            if match:
                value = match.group(1).strip()
                # Format currency fields consistently
                if any(x in field for x in ['Amount', 'Charge', 'VAT']):
                    value = f"ETB {value}"
                result[field] = value

        # Clean and format specific fields
        if 'Transaction Date' in result:
            try:
                dt = datetime.strptime(
                    result['Transaction Date'], "%b %d, %Y, %I:%M:%S %p")
                result['Transaction Date'] = dt.isoformat()
            except ValueError:
                pass

        return result

    except Exception as e:
        print(f"Error processing Zemen receipt: {str(e)}")
        return None
