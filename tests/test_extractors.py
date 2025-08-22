import pytest
from ethiobank_receipts import extract_receipt


def test_extract_cbe():
    url = "https://apps.cbe.com.et:100/?id=FT25211G11JQ21827223"
    result = extract_receipt("cbe", url)
    assert isinstance(result, dict)
    assert "customer_name" in result


def test_extract_dashen():
    url = "https://receipt.dashensuperapp.com/receipt/387ETAP2522000WK"
    result = extract_receipt("dashen", url)
    assert isinstance(result, dict)
    assert "sender_name" in result


def test_extract_awash():
    url = "https://awashpay.awashbank.com:8225/-E41AE0D86FFA-21XYYW"
    result = extract_receipt("awash", url)
    assert isinstance(result, dict)
    assert "Amount" in result


@pytest.mark.skip(reason="Requires Selenium + ChromeDriver")
def test_extract_boa():
    url = "https://cs.bankofabyssinia.com/slip/?trx=FT252113TRLT13487"
    result = extract_receipt("boa", url)
    assert isinstance(result, dict)
    assert "Source Account" in result


def test_extract_zemen():
    url = "https://share.zemenbank.com/rt/94497018108ATWR2520600HM/pdf"
    result = extract_receipt("zemen", url)
    assert isinstance(result, dict)
    assert "Invoice No" in result


def test_extract_cbe_from_ft_helper():
    # Ensure the helper builds the URL correctly and delegates to the extractor
    from ethiobank_receipts.extractors.cbe import extract_cbe_receipt_info_from_ft

    result = extract_cbe_receipt_info_from_ft("FT25211G11JQ", "21827223")
    assert isinstance(result, dict)
    assert "customer_name" in result
