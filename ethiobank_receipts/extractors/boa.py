import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from typing import Dict, Optional


def extract_boa_receipt_data(url: str) -> Dict[str, Optional[str]]:
    """
    Extract receipt data from Bank of Abyssinia online receipt page.

    Args:
        url (str): Receipt page URL.

    Returns:
        Dict[str, Optional[str]]: Extracted receipt fields.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)  # Wait for page load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    rows = soup.select("table tr")
    data = {}
    for row in rows:
        tds = row.find_all("td")
        if len(tds) == 2:
            key = tds[0].get_text(strip=True).rstrip(":")
            value = tds[1].get_text(strip=True)
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
        "Narrative": data.get("Narrative"),
    }
