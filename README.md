# ethiobank-receipts

**🔍 Fast and Reliable Receipt Extraction from Ethiopian Banks**

Optimized for speed and accuracy, `ethiobank-receipts` enables developers to extract structured data from digital bank receipts across major Ethiopian banks using multithreading and connection pooling.

## 🚀 Features

- 🏦 **Supports Major Ethiopian Banks**  
  Currently supports:

  - Commercial Bank of Ethiopia (CBE)
  - Dashen Bank
  - Awash Bank
  - Bank of Abyssinia (BOA)
  - Zemen Bank

- ⚡ **High Performance**

  - Multithreaded PDF parsing for faster processing
  - Optimized network handling with `requests.Session` for connection pooling

- 🧠 **Smart Automation**

  - Chrome WebDriver caching to avoid redundant browser launches (used for BOA receipts)

- 🧪 **Developer Friendly**
  - Easy-to-use CLI interface
  - Built-in test suite for validation

## 📦 Installation

Install via pip:

```bash
pip install ethiobank-receipts
```

## 📖 Usage Example

```python

from ethiobank_receipts import extract_receipt
from pprint import pprint
# Example URLs for each supported bank (replace with actual receipt URLs)
urls = {
    "cbe": "https://apps.cbe.com.et:100/?id=FT*************",
    "dashen": "https://receipt.dashensuperapp.com/receipt/**************",
    "awash": "https://awashpay.awashbank.com:8225/-*****************",
    "boa": "https://cs.bankofabyssinia.com/slip/?trx=****************",
    "zemen": "https://share.zemenbank.com/rt/****************/pdf"
}

for bank, url in urls.items():
    print(f"Extracting receipt data from {bank}...")
    try:
        result = extract_receipt(bank, url)
        pprint(result)
    except Exception as e:
        pprint(f"Failed to extract from {bank}: {e}")

```

## 🧩 CBE quick helper: FT + account last 8 digits

If you have the CBE FT number and the account number (or just its last 8 digits), you can skip manual URL building and use the helper:

```python
from ethiobank_receipts.extractors.cbe import extract_cbe_receipt_info_from_ft

# FT number + last 8 digits of the account
data = extract_cbe_receipt_info_from_ft("FT25211G11JQ", "21827223")
print(data)
```

Notes:

- The helper uppercases the FT and ignores spaces.
- It will take the last 8 digits from whatever account string you pass (full or partial). If fewer than 8 digits are provided, it raises a ValueError.
