from .extractors import cbe, dashen, awash, boa, zemen, tele

EXTRACTORS = {
    "cbe": cbe.extract_cbe_receipt_info,
    "dashen": dashen.extract_dashen_receipt_data,
    "awash": awash.extract_awash_receipt_data,
    "boa": boa.extract_boa_receipt_data,
    "zemen": zemen.extract_zemen_receipt_data,
    "tele": tele.extract_tele_receipt_data,
}


def extract_receipt(bank: str, url: str):
    """
    Extract receipt data from a given Ethiopian bank receipt URL.

    Args:
        bank (str): One of: cbe, dashen, awash, boa, zemen
        url (str): PDF or HTML receipt URL

    Returns:
        dict: Extracted receipt fields
    """
    bank = bank.lower()
    if bank not in EXTRACTORS:
        raise ValueError(f"Unsupported bank: {bank}")
    return EXTRACTORS[bank](url)
