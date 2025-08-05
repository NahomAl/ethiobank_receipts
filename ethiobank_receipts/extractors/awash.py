import requests
from bs4 import BeautifulSoup
from typing import Dict


def extract_awash_receipt_data(url: str) -> Dict[str, str]:
    """
    Extract receipt data from Awash Bank web-based receipt page.

    Args:
        url (str): Receipt page URL.

    Returns:
        Dict[str, str]: Extracted receipt fields.
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("table.info-table tr")

    data = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 3:
            key = cells[0].get_text(strip=True).replace(":", "")
            value = cells[2].get_text(strip=True)
            data[key] = value

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

    return {k: v for k, v in data.items() if k in keys_of_interest}
