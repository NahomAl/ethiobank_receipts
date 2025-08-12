import requests
from bs4 import BeautifulSoup
from typing import Dict

session = requests.Session()

def extract_awash_receipt_data(url):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("table.info-table tr")

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
