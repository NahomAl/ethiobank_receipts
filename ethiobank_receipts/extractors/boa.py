import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from functools import lru_cache


@lru_cache(maxsize=1)
def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


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
