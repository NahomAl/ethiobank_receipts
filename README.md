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
  - Telebirr (Ethio telecom)

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
  "zemen": "https://share.zemenbank.com/rt/****************/pdf",
  # Telebirr accepts either a full URL or just the ID (e.g., CHQ0FJ403O)
  "tele": "CHQ0FJ403O",
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

## 📱 Telebirr usage

You can pass either a full URL or just the receipt ID:

```python
from ethiobank_receipts import extract_receipt

# With full URL
data1 = extract_receipt("tele", "https://transactioninfo.ethiotelecom.et/receipt/CHQ0FJ403O")

# Or just the ID
data2 = extract_receipt("tele", "CHQ0FJ403O")
```

## 🧰 CLI usage

URL-based (all banks):

```bash
python -m ethiobank_receipts.cli cbe "https://apps.cbe.com.et:100/?id=FT25211G11JQ21827223"
python -m ethiobank_receipts.cli dashen "https://receipt.dashensuperapp.com/receipt/387ETAP2522000WK"
python -m ethiobank_receipts.cli tele CHQ0FJ403O    # ID also works
```

CBE helper (build URL from FT + account):

```bash
python -m ethiobank_receipts.cli cbe --ft FT25211G11JQ --account 21827223
```
