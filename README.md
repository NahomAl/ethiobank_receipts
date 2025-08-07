# ethiobank-receipts

**🔍 Fast and Reliable Receipt Extraction from Ethiopian Banks**

Optimized for speed and accuracy, `ethiobank-receipts` enables developers to extract structured data from digital bank receipts across major Ethiopian banks using multithreading and connection pooling.

---

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

---

## 📦 Installation

Install via pip:

```bash
pip install ethiobank-receipts
