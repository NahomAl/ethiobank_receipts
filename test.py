"""Optimized receipt extraction for Ethiopian banks using connection pooling """
import re
import time
import requests
import tempfile
import pdfplumber
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global session for connection pooling
session = requests.Session()


def download_pdf_from_url(url, verify_ssl=False):
    """Downloads a PDF from a URL and saves it to a temp file with connection pooling."""
    response = session.get(url, verify=verify_ssl)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

# Cache browser instance for BOA to avoid recreating it

@lru_cache(maxsize=1)
def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# --- CBE ---


def extract_cbe_receipt_info(url):
    pdf_path = download_pdf_from_url(url, verify_ssl=False)

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

# --- Dashen ---


def extract_dashen_receipt_data(url):
    pdf_path = download_pdf_from_url(url, verify_ssl=False)

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

# --- Awash ---


def extract_awash_receipt_data(url):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("table.info-table tr")

    # Use list comprehension for faster processing
    data = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 3:
            key = cells[0].text.strip().rstrip(":")
            value = cells[2].text.strip()
            data[key] = value

    keys_of_interest = [
        "Transaction Time", "Transaction Type", "Amount", "Charge", "VAT",
        "Sender Name", "Sender Account", "Beneficiary name", "Beneficiary Account",
        "Beneficiary Bank", "Reason", "Transaction ID"
    ]

    return {k: data.get(k) for k in keys_of_interest}

# --- BOA ---


def extract_boa_receipt_data(url):
    driver = get_chrome_driver()
    driver.get(url)
    # Reduced sleep time with explicit wait would be better
    time.sleep(2)  # Reduced from 3 seconds

    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Optimized table parsing
        data = {}
        for row in soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                key = cells[0].text.strip().rstrip(":")
                value = cells[1].text.strip()
                data[key] = value

        return {
            "Source Account": data.get("Source Account"),
            "Source Account Name": data.get("Source Account Name"),
            "Receiver's Account": data.get("Receiver's Account"),
            "Receiver's Name": data.get("Receiver's Name"),
            "Transferred Amount": data.get("Transferred amount"),
            "Service Charge": data.get("Service Charge"),
            "VAT": data.get("VAT (15%)"),
            "Total Amount": data.get("Total Amount"),
            "Transaction Type": data.get("Transaction Type"),
            "Transaction Date": data.get("Transaction Date"),
            "Transaction Reference": data.get("Transaction Reference"),
            "Narrative": data.get("Narrative")
        }
    finally:
        # Don't quit the driver, keep it for reuse
        pass

# --- Zemen ---


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


# Example usage
if __name__ == "__main__":
    from pprint import pprint
    urls = [
        ("CBE", "https://apps.cbe.com.et:100/?id=FT25211G11JQ21827223",
         extract_cbe_receipt_info),
        ("Dashen", "https://receipt.dashensuperapp.com/receipt/099WDTS2515400WH",
         extract_dashen_receipt_data),
        ("Awash", "https://awashpay.awashbank.com:8225/-E41AE0D86FFA-21XYYW",
         extract_awash_receipt_data),
        ("Zemen", "https://share.zemenbank.com/rt/94497018108ATWR2520600HM/pdf",
         extract_zemen_receipt_data),
        ("BOA", "https://cs.bankofabyssinia.com/slip/?trx=FT252113TRLT13487",
         extract_boa_receipt_data),
    ]
    for bank, url, func in urls:
        print(f"--- {bank} Receipt ---")
        try:
            pprint(func(url))
        except Exception as e:
            print(f"Error extracting {bank}: {e}")
        print("\n")
