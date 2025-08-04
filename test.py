"""This script downloads a PDF receipt from the Central Bank of Ethiopia's website,
"""
import pdfplumber
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime
import re
import tempfile
import requests
import pdfplumber
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# CBE

def download_pdf_from_url(url):
    """Downloads the PDF from a given URL and saves it to a temp file."""
    response = requests.get(url, verify=False)
    response.raise_for_status()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file.write(response.content)
    tmp_file.close()
    return tmp_file.name

def extract_cbe_receipt_info(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    def extract(pattern, text, group=1, default=None):
        match = re.search(pattern, text)
        return match.group(group).strip() if match else default

    data = {
        "customer_name": extract(r"Customer Name:\s*(.+)", full_text),
        "branch": extract(r"Branch:\s*(.+)", full_text),
        "region_city": extract(r"Region:\s*(.*?)\n", full_text),
        "payment_date": extract(r"Payment Date & Time\s*([\d\/:,\sAPMapm]+)", full_text),
        "reference_no": extract(r"Reference No.*?([A-Z0-9]+)", full_text),
        "payer": extract(r"Payer\s+([A-Z\s]+)", full_text),
        "payer_account": extract(r"Payer\s+[A-Z\s]+\nAccount\s+([\d\*]+)", full_text),
        "receiver": extract(r"Receiver\s+([A-Z\s]+)", full_text),
        "receiver_account": extract(r"Receiver\s+[A-Z\s]+\nAccount\s+([\d\*]+)", full_text),
        "service": extract(r"Reason / Type of service\s+(.+)", full_text),
        "transferred_amount": extract(r"Transferred Amount\s+([\d,.]+) ETB", full_text),
        "commission": extract(r"Commission or Service Charge\s+([\d,.]+) ETB", full_text),
        "vat_on_commission": extract(r"15% VAT on Commission\s+([\d,.]+) ETB", full_text),
        "total_debited": extract(r"Total amount debited from customers account\s+([\d,.]+) ETB", full_text),
        "amount_in_words": extract(r"Amount in Word ETB\s+(.+)", full_text)
    }

    try:
        data["payment_date"] = datetime.strptime(data["payment_date"], "%m/%d/%Y, %I:%M:%S %p").isoformat()
    except:
        pass

    return data

if __name__ == "__main__":
    url = "https://apps.cbe.com.et:100/?id=FT25211G11JQ21827223"

    try:
        pdf_path = download_pdf_from_url(url)
        receipt_data = extract_cbe_receipt_info(pdf_path)

        from pprint import pprint
        pprint(receipt_data)
    except Exception as e:
        print(f"Error: {e}")


# Dashen Super Receipt Extraction

def download_pdf(url):
    """Download PDF from URL and save to temp file."""
    response = requests.get(url, verify=False)  # Add verify=True if SSL works
    response.raise_for_status()
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file.write(response.content)
    tmp_file.close()
    return tmp_file.name


def extract_dashen_receipt(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text()
                         for page in pdf.pages if page.extract_text()])

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

    # Try parsing date
    try:
        dt = datetime.strptime(
            data["transaction_date"], "%b %d, %Y, %I:%M:%S %p")
        data["transaction_date"] = dt.isoformat()
    except Exception:
        pass

    return data


if __name__ == "__main__":
    # <-- put actual .pdf link if direct
    url = "https://receipt.dashensuperapp.com/receipt/099WDTS2515400WH"
    try:
        pdf_file = download_pdf(url)
        result = extract_dashen_receipt(pdf_file)
        from pprint import pprint
        pprint(result)
    except Exception as e:
        print(f"Error: {e}")


#Awash

def extract_awash_receipt_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("table.info-table tr")

    data = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 3:
            key = cells[0].get_text(strip=True).replace(":", "")
            value = cells[2].get_text(strip=True)
            data[key] = value

    # Filter only the relevant fields
    keys_of_interest = [
        "Transaction Time",
        "Transaction Type",
        "Amount",
        "Charge",
        "VAT",
        "Sender Name",
        "Sender Account",
        "Beneficiary name",
        "Beneficiary Account",
        "Beneficiary Bank",
        "Reason",
        "Transaction ID",
    ]

    filtered_data = {k: v for k, v in data.items() if k in keys_of_interest}
    return filtered_data

url = "https://awashpay.awashbank.com:8225/-E41AE0D86FFA-21XYYW"
receipt_data = extract_awash_receipt_data(url)


for key, value in receipt_data.items():
    print(f"{key}: {value}")


# Abyssinia Bank

def extract_boa_receipt_data(url):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Start Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Wait for page to load content (increase if slow network)
    time.sleep(3)

    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Close driver
    driver.quit()

    # Extract data from table
    rows = soup.select("table tr")
    data = {}
    for row in rows:
        tds = row.find_all("td")
        if len(tds) == 2:
            key = tds[0].get_text(strip=True).rstrip(":")
            value = tds[1].get_text(strip=True)
            data[key] = value

    # Return structured dictionary
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
        "Narrative": data.get("Narrative"),
    }


# Example usage
url = "https://cs.bankofabyssinia.com/slip/?trx=FT252113TRLT13487"
receipt_data = extract_boa_receipt_data(url)

# Print extracted data
for key, value in receipt_data.items():
    print(f"{key}: {value}")


# Zemen Bank

def extract_zemen_receipt_data_from_url(pdf_url):
    # Download the PDF to a temp file
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    # Now extract data from the temp file
    return extract_zemen_receipt_data(tmp_path)

def extract_zemen_receipt_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text()
                         for page in pdf.pages if page.extract_text())

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Extract fields using regex/keywords
    data = {}

    # Invoice No
    m = re.search(r'Invoice No\.?:\s*([0-9]+)', text, re.IGNORECASE)
    if m:
        data['Invoice No'] = m.group(1)

    # Date
    m = re.search(r'Date[:\s]+([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})', text)
    if m:
        data['Date'] = m.group(1)

    # Payer name
    m = re.search(r'Payer name:\s*([A-Z\s]+)', text)
    if m:
        data['Payer Name'] = m.group(1).strip()

    # Payer account
    m = re.search(r'Payer account no\.:\s*([\d\*()X]+)', text)
    if m:
        data['Payer Account No'] = m.group(1).strip()

    # Recipient name
    m = re.search(r'Recipient name:\s*([A-Za-z\s\.]+)', text)
    if m:
        data['Recipient Name'] = m.group(1).strip()

    # Recipient account
    m = re.search(r'Recipient account no\.:\s*([\d\*]+)', text)
    if m:
        data['Recipient Account No'] = m.group(1).strip()

    # Reference No
    m = re.search(r'Reference No:\s*([A-Z0-9]+)', text)
    if m:
        data['Reference No'] = m.group(1).strip()

    # Transaction status
    m = re.search(r'Transaction status:\s*(\w+)', text)
    if m:
        data['Transaction Status'] = m.group(1).strip()

    # Transaction detail
    m = re.search(r'Transaction Detail\s+([A-Za-z\s\-]+)\s+ETB', text)
    if m:
        data['Transaction Detail'] = m.group(1).strip()

    # Settled Amount
    m = re.search(r'ATM CASH WITHDRAWAL ETB\s*([\d,]+\.\d{2})', text)
    if m:
        data['Settled Amount'] = "ETB " + m.group(1)

    # Service Charge
    m = re.search(r'Service Charge ETB\s*([\d,]+\.\d{2})', text)
    if m:
        data['Service Charge'] = "ETB " + m.group(1)

    # VAT
    m = re.search(r'VAT 15% ETB\s*([\d,]+\.\d{2})', text)
    if m:
        data['VAT'] = "ETB " + m.group(1)

    # Total Amount Paid
    m = re.search(r'Total Amount Paid ETB\s*([\d,]+\.\d{2})', text)
    if m:
        data['Total Amount Paid'] = "ETB " + m.group(1)

    # Total in words
    m = re.search(r'Total amount in word:\s*([A-Z\s\-]+CENT\(S\))', text)
    if m:
        data['Amount in Words'] = m.group(1).title()

    return data



url = "https://share.zemenbank.com/rt/94497018108ATWR2520600HM/pdf"
receipt_data = extract_zemen_receipt_data_from_url(url)

for k, v in receipt_data.items():
    print(f"{k}: {v}")
