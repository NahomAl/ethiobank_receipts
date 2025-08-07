import re
from datetime import datetime
import pdfplumber
from concurrent.futures import ThreadPoolExecutor
from ethiobank_receipts.download import download_pdf_from_url


def extract_dashen_receipt_data(url):
    pdf_path = download_pdf_from_url(url)

    # Extract text from PDF in parallel
    def extract_page_text(page):
        return page.extract_text()

    with pdfplumber.open(pdf_path) as pdf:
        with ThreadPoolExecutor() as executor:
            texts = list(executor.map(extract_page_text, pdf.pages))
        text = "\n".join(text for text in texts if text)

    # Precompile all regex patterns
    patterns = {
        "sender_name": re.compile(r"Account Holder Name:\s*(.+?)\n"),
        "channel": re.compile(r"Transaction Channel:\s*(.+?)\n"),
        "service_type": re.compile(r"Service Type:\s*(.+?)\n"),
        "narrative": re.compile(r"Narrative:\s*(.+?)\n"),
        "beneficiary_name": re.compile(r"Account Holder Name:\s*(.+?)\n"),
        "beneficiary_account": re.compile(r"Account Number:\s*(\d+)"),
        "beneficiary_bank": re.compile(r"Institution Name:\s*(.+?)\n"),
        "transfer_reference": re.compile(r"Transfer Reference:\s*(.+?)\n"),
        "transaction_reference": re.compile(r"Transaction Ref:\s*(.+?)\n"),
        "transaction_date": re.compile(r"Date:\s*(.+?)\n"),
        "amount": re.compile(r"Transaction Amount\s*([\d,.]+) ETB"),
        "total": re.compile(r"Total\s*([\d,.]+) ETB"),
        "amount_in_words": re.compile(r"Amount in words:\s*(.+?)\n")
    }

    data = {key: (pattern.search(text).group(1).strip() if pattern.search(text) else None)
            for key, pattern in patterns.items()}

    try:
        dt = datetime.strptime(
            data["transaction_date"], "%b %d, %Y, %I:%M:%S %p")
        data["transaction_date"] = dt.isoformat()
    except:
        pass

    return data
