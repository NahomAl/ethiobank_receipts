""" Download PDF from URL and return local path. """
import requests
import tempfile

session = requests.Session()

def download_pdf_from_url(url, verify_ssl=False):
    """Downloads a PDF from a URL and saves it to a temp file with connection pooling."""
    response = session.get(url, verify=verify_ssl)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name
