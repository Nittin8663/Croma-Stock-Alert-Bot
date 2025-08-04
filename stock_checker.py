import requests
from bs4 import BeautifulSoup

def is_in_stock(croma_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(croma_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Adjust this selector if Croma's page structure changes
    return not bool(soup.find(string=lambda t: "Sold Out" in t or "Out of Stock" in t))
