""" Download PDF from URL and return local path. """
import requests
import tempfile


def download_pdf(url: str, verify_ssl: bool = False) -> str:
    """Download PDF from URL and return local path."""
    response = requests.get(url, verify=verify_ssl)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        return tmp.name
