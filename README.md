# 📄 ethiobank-receipts

**🔍 Fast and Reliable Receipt Extraction from Ethiopian Banks**  
Optimized for speed and accuracy, `ethiobank-receipts` enables developers to extract structured data from digital bank receipts across major Ethiopian banks using multithreading and connection pooling.

---

## ⚠️ Disclaimer
This is **not an official Python packages**.  
I am not affiliated with **Ethio Telecom**, **Telebirr**, or any Ethiopian bank (CBE, Dashen, Awash, BOA, Zemen).  

This package is built purely for **developer utility and research purposes** and works by scraping publicly available receipt data.

---

## ✅ Features

- 🏦 **Bank Support**
  - Commercial Bank of Ethiopia (CBE)  
  - Dashen Bank  
  - Awash Bank  
  - Bank of Abyssinia (BOA)  
  - Zemen Bank  
  - Telebirr (Ethio telecom)  

- ⚡ **High Performance**
  - Multithreaded PDF parsing  
  - Optimized HTTP connection pooling (`requests.Session`)  

- 🧠 **Smart Automation**
  - Chrome WebDriver caching (for BOA receipts)  

- 🧪 **Developer Friendly**
  - Easy CLI interface  
  - Built-in test suite  

---

## 📦 Installation

```bash
pip install ethiobank-receipts
````

---

## 📖 Usage (Python)

### Extract from Any Bank by URL

```python
from ethiobank_receipts import extract_receipt
from pprint import pprint

urls = {
    "cbe": "https://apps.cbe.com.et:100/?id=FT*************",
    "dashen": "https://receipt.dashensuperapp.com/receipt/**************",
    "awash": "https://awashpay.awashbank.com:8225/-*****************",
    "boa": "https://cs.bankofabyssinia.com/slip/?trx=****************",
    "zemen": "https://share.zemenbank.com/rt/****************/pdf",
    "tele": "CHQ0FJ403O"
}

for bank, url in urls.items():
    print(f"Extracting from {bank}...")
    try:
        result = extract_receipt(bank, url)
        pprint(result)
    except Exception as e:
        pprint(f"Failed: {e}")
```

---

### Extract CBE with FT Number + Account

```python
from ethiobank_receipts.extractors.cbe import extract_cbe_receipt_info_from_ft

data = extract_cbe_receipt_info_from_ft("FT25211G11JQ", "21827223")
print(data)
```

✔ Normalizes FT format (uppercase, trims spaces)
✔ Uses last 8 digits of account
❌ Raises `ValueError` if account digits < 8

---

### Extract Telebirr by URL or Receipt ID

```python
from ethiobank_receipts import extract_receipt

# With full URL
data1 = extract_receipt("tele", "https://transactioninfo.ethiotelecom.et/receipt/CHQ0FJ403O")

# Or just the ID
data2 = extract_receipt("tele", "CHQ0FJ403O")
```

---

## 🧰 CLI Usage

### URL-based (all banks)

```bash
python -m ethiobank_receipts.cli cbe "https://apps.cbe.com.et:100/?id=FT25211G11JQ21827223"
python -m ethiobank_receipts.cli dashen "https://receipt.dashensuperapp.com/receipt/387ETAP2522000WK"
python -m ethiobank_receipts.cli tele CHQ0FJ403O
```

### CBE helper

```bash
python -m ethiobank_receipts.cli cbe --ft FT25211G11JQ --account 21827223
```

---

## 📄 Sample Outputs

### CBE Receipt

```json
{
  "payer_name": "John Doe",
  "payer_account": "1000223344",
  "receiver_name": "XYZ Trading PLC",
  "receiver_account": "1000556677",
  "amount": 1250.75,
  "currency": "ETB",
  "date": "2025-09-09T10:20:00",
  "reference": "FT25211G11JQ",
  "status": "SUCCESS"
}
```

### Telebirr Receipt

```json
{
  "payer_phone": "0912345678",
  "receiver_name": "ABC Market",
  "receiver_account": "1000123456",
  "amount": 500.00,
  "currency": "ETB",
  "date": "2025-09-09T09:10:00",
  "reference": "CHQ0FJ403O",
  "status": "SUCCESS"
}
```

### Dashen Bank Receipt

```json
{
  "payer_name": "Jane Doe",
  "payer_account": "2000112233",
  "receiver_name": "FastPay PLC",
  "receiver_account": "2000556677",
  "amount": 750.25,
  "currency": "ETB",
  "date": "2025-09-09T11:30:00",
  "reference": "387ETAP2522000WK",
  "status": "SUCCESS"
}
```

### Awash Bank Receipt

```json
{
  "payer_name": "Michael Abebe",
  "payer_account": "3000334455",
  "receiver_name": "Utility Service",
  "receiver_account": "3000667788",
  "amount": 980.00,
  "currency": "ETB",
  "date": "2025-09-09T08:45:00",
  "reference": "AW25220099888",
  "status": "SUCCESS"
}
```

### BOA Receipt

```json
{
  "payer_name": "Sarah Mekonnen",
  "payer_account": "4000445566",
  "receiver_name": "E-Store Ethiopia",
  "receiver_account": "4000998877",
  "amount": 1500.00,
  "currency": "ETB",
  "date": "2025-09-09T14:15:00",
  "reference": "BOA123456789",
  "status": "SUCCESS"
}
```

### Zemen Bank Receipt

```json
{
  "payer_name": "Daniel Kebede",
  "payer_account": "5000556677",
  "receiver_name": "XYZ Imports",
  "receiver_account": "5000112233",
  "amount": 2000.00,
  "currency": "ETB",
  "date": "2025-09-09T16:00:00",
  "reference": "ZM987654321",
  "status": "SUCCESS"
}
```

---

## 🌐 Hosting Limitations

Some receipt systems have **regional restrictions**:

* **Telebirr** often blocks or times out requests from **foreign IPs**.

  * Errors include: `403`, `ERR_FAILED`, or DNS resolution issues.
  * ❌ Affected: VPS or cloud servers outside Ethiopia (e.g., AWS, Hetzner).
  * ✅ Works Best: Servers hosted in Ethiopia (e.g., Ethio Telecom hosting, TeleCloud VPS).

* **Bank of Abyssinia (BOA)** receipts require **Chrome WebDriver**.
  The extractor caches driver sessions for performance.

---

## 🛠 Notes

* Always provide the correct **reference number** or **receipt URL**.
* For CBE, you may use **FT number + last 8 digits of account** instead of full URL.
* If fewer than 8 digits are provided for CBE accounts, a `ValueError` is raised.

---

## 📜 License

MIT License — see [LICENSE](https://opensource.org/license/mit).