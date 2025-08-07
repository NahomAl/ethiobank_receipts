import argparse
from ethiobank_receipts import extract_receipt


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured bank receipt data from URL.")
    parser.add_argument(
        "bank", choices=["cbe", "dashen", "awash", "boa", "zemen"], help="Bank name")
    parser.add_argument("url", help="Receipt PDF or HTML URL")
    args = parser.parse_args()

    try:
        result = extract_receipt(args.bank, args.url)
        for k, v in result.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
