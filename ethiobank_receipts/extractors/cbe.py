from datetime import datetime
import re
import pdfplumber
import re
import pdfplumber
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from ethiobank_receipts.download import download_pdf_from_url

def extract_cbe_receipt_info(url):
    pdf_path = download_pdf_from_url(url, verify_ssl=True)

    # Use parallel processing for PDF text extraction if it's a multi-page document
    def extract_page_text(page):
        return page.extract_text()

    with pdfplumber.open(pdf_path) as pdf:
        with ThreadPoolExecutor() as executor:
            texts = list(executor.map(extract_page_text, pdf.pages))
        full_text = "\n".join(text for text in texts if text)

    # Precompile all regex patterns
    patterns = {
        "customer_name": re.compile(r"Customer Name:\s*(.+)"),
        "branch": re.compile(r"Branch:\s*(.+)"),
        "region_city": re.compile(r"Region:\s*(.*?)\n"),
        "payment_date": re.compile(r"Payment Date & Time\s*([\d/:,\sAPMapm]+)"),
        "reference_no": re.compile(r"Reference No.*?([A-Z0-9]+)"),
        "payer": re.compile(r"Payer\s+([A-Z\s]+)"),
        "payer_account": re.compile(r"Payer\s+[A-Z\s]+\nAccount\s+([\d\*]+)"),
        "receiver": re.compile(r"Receiver\s+([A-Z\s]+)"),
        "receiver_account": re.compile(r"Receiver\s+[A-Z\s]+\nAccount\s+([\d\*]+)"),
        "service": re.compile(r"Reason / Type of service\s+(.+)"),
        "transferred_amount": re.compile(r"Transferred Amount\s+([\d,.]+) ETB"),
        "commission": re.compile(r"Commission or Service Charge\s+([\d,.]+) ETB"),
        "vat_on_commission": re.compile(r"15% VAT on Commission\s+([\d,.]+) ETB"),
        "total_debited": re.compile(r"Total amount debited from customers account\s+([\d,.]+) ETB"),
        "amount_in_words": re.compile(r"Amount in Word ETB\s+(.+)")
    }

    data = {key: (pattern.search(full_text).group(1).strip() if pattern.search(full_text) else None)
            for key, pattern in patterns.items()}

    try:
        data["payment_date"] = datetime.strptime(
            data["payment_date"], "%m/%d/%Y, %I:%M:%S %p").isoformat()
    except:
        pass

    return data
