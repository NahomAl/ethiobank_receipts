from datetime import datetime
import re
import pdfplumber
from typing import Dict, Optional


def extract_cbe_receipt_info(pdf_path: str) -> Dict[str, Optional[str]]:
    """
    Extract structured receipt information from a Central Bank of Ethiopia PDF receipt.

    Args:
        pdf_path (str): Local path to the PDF file.

    Returns:
        Dict[str, Optional[str]]: Dictionary with extracted fields.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    def extract(pattern, group=1, default=None):
        match = re.search(pattern, text)
        return match.group(group).strip() if match else default

    data = {
        "customer_name": extract(r"Customer Name:\s*(.+)"),
        "branch": extract(r"Branch:\s*(.+)"),
        "region_city": extract(r"Region:\s*(.*?)\n"),
        "payment_date": extract(r"Payment Date & Time\s*([\d\/:,\sAPMapm]+)"),
        "reference_no": extract(r"Reference No.*?([A-Z0-9]+)"),
        "payer": extract(r"Payer\s+([A-Z\s]+)"),
        "payer_account": extract(r"Payer\s+[A-Z\s]+\nAccount\s+([\d\*]+)"),
        "receiver": extract(r"Receiver\s+([A-Z\s]+)"),
        "receiver_account": extract(r"Receiver\s+[A-Z\s]+\nAccount\s+([\d\*]+)"),
        "service": extract(r"Reason / Type of service\s+(.+)"),
        "transferred_amount": extract(r"Transferred Amount\s+([\d,.]+) ETB"),
        "commission": extract(r"Commission or Service Charge\s+([\d,.]+) ETB"),
        "vat_on_commission": extract(r"15% VAT on Commission\s+([\d,.]+) ETB"),
        "total_debited": extract(r"Total amount debited from customers account\s+([\d,.]+) ETB"),
        "amount_in_words": extract(r"Amount in Word ETB\s+(.+)")
    }

    try:
        data["payment_date"] = datetime.strptime(
            data["payment_date"], "%m/%d/%Y, %I:%M:%S %p").isoformat()
    except Exception:
        pass

    return data
