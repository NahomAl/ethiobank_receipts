"""Command-line interface for extracting Ethiopian bank receipt data."""
import argparse
from .download import download_pdf
from .extractors import cbe, dashen, awash, boa, zemen

EXTRACTORS = {
    "cbe": cbe.extract_cbe_receipt_info,
    "dashen": dashen.extract_dashen_receipt,
    "awash": awash.extract_awash_receipt_data,
    "boa": boa.extract_boa_receipt_data,
    "zemen": zemen.extract_zemen_receipt_data,
}


def main():
    parser = argparse.ArgumentParser(
        description="Extract Ethiopian bank receipt data.")
    parser.add_argument("bank", choices=EXTRACTORS.keys())
    parser.add_argument("url", help="Receipt PDF or page URL")
    args = parser.parse_args()

    pdf_path = download_pdf(args.url)
    result = EXTRACTORS[args.bank](pdf_path)
    print(result)


if __name__ == "__main__":
    main()
