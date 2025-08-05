import re
from datetime import datetime
import pdfplumber
from typing import Dict, Optional


def extract_dashen_receipt(pdf_path: str) -> Dict[str, Optional[str]]:
    """
    Extract receipt data from Dashen Super App PDF receipts.

    Args:
        pdf_path (str): Path to downloaded PDF file.

    Returns:
        Dict[str, Optional[str]]: Extracted fields.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() or "" for page in pdf.pages])

    def extract(pattern, group=1):
        match = re.search(pattern, text)
        return match.group(group).strip() if match else None

    data = {
        "sender_name": extract(r"Account Holder Name:\s*(.+?)\n"),
        "channel": extract(r"Transaction Channel:\s*(.+?)\n"),
        "service_type": extract(r"Service Type:\s*(.+?)\n"),
        "narrative": extract(r"Narrative:\s*(.+?)\n"),
        "beneficiary_name": extract(r"Beneficiary's Details\s*Account Holder Name:\s*(.+?)\n"),
        "beneficiary_account": extract(r"Account Number:\s*(\d+)"),
        "beneficiary_bank": extract(r"Institution Name:\s*(.+?)\n"),
        "transfer_reference": extract(r"Transfer Reference:\s*(.+?)\n"),
        "transaction_reference": extract(r"Transaction Ref:\s*(.+?)\n"),
        "transaction_date": extract(r"Date:\s*(.+?)\n"),
        "amount": extract(r"Transaction Amount\s*([\d,.]+) ETB"),
        "total": extract(r"Total\s*([\d,.]+) ETB"),
        "amount_in_words": extract(r"Amount in words:\s*(.+?)\n"),
    }

    # Parse date
    try:
        data["transaction_date"] = datetime.strptime(
            data["transaction_date"], "%b %d, %Y, %I:%M:%S %p"
        ).isoformat()
    except Exception:
        pass

    return data
