import re
import pdfplumber
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from ethiobank_receipts.download import download_pdf_from_url


def extract_cbe_receipt_info(url):
    pdf_path = download_pdf_from_url(url)

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

    payment_date_str = data.get("payment_date")
    if payment_date_str:
        try:
            data["payment_date"] = datetime.strptime(
                payment_date_str, "%m/%d/%Y, %I:%M:%S %p"
            ).isoformat()
        except (ValueError, TypeError):
            pass

    return data


def extract_cbe_receipt_info_from_ft(ft_number: str, account_last8_or_full: str):
    """
    Build the CBE receipt URL from the FT number and account digits and extract receipt info.

    Inputs:
    - ft_number: e.g., "FT25211G11JQ" (case-insensitive, spaces ignored)
    - account_last8_or_full: last eight digits (e.g., "21827223") or a full account number

    Returns:
    - Dict with extracted receipt fields (same as extract_cbe_receipt_info)
    """
    # Normalize FT number (remove spaces, uppercase)
    ft = re.sub(r"\s+", "", ft_number or "").upper()

    # Keep only digits from the account input and take the last 8
    digits = re.sub(r"\D", "", account_last8_or_full or "")
    if len(digits) < 8:
        raise ValueError("Account number must contain at least 8 digits")
    last8 = digits[-8:]

    url = f"https://apps.cbe.com.et:100/?id={ft}{last8}"
    return extract_cbe_receipt_info(url)
