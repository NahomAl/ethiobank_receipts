import argparse
import requests
from ethiobank_receipts import extract_receipt


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract structured bank receipt data.\n"
            "- Default: pass a receipt URL for any bank.\n"
            "- CBE: alternatively pass --ft and --account to build the URL automatically."
        )
    )
    parser.add_argument(
        "bank", choices=["cbe", "dashen", "awash", "boa", "zemen", "tele"], help="Bank name")
    # URL is optional if using CBE --ft/--account
    parser.add_argument("url", nargs="?", help="Receipt PDF or HTML URL")
    parser.add_argument("--ft", help="CBE FT reference (e.g., FT25211G11JQ)")
    parser.add_argument(
        "--account",
        help="CBE account number or last 8 digits (used with --ft)",
    )
    args = parser.parse_args()

    try:
        if args.bank == "cbe" and args.ft:
            if not args.account:
                raise ValueError(
                    "--account is required when using --ft for CBE")
            # Lazy import to avoid unnecessary dependency edges for other banks
            from ethiobank_receipts.extractors.cbe import (
                extract_cbe_receipt_info_from_ft,
            )

            result = extract_cbe_receipt_info_from_ft(args.ft, args.account)
        else:
            if not args.url:
                raise ValueError(
                    "url (or ID for tele) is required unless using --ft and --account for CBE"
                )
            result = extract_receipt(args.bank, args.url)

        for k, v in result.items():
            print(f"{k}: {v}")
    except (ValueError, requests.RequestException) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
