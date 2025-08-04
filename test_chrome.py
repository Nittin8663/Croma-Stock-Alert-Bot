from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile

options = Options()
options.binary_location = "/usr/bin/google-chrome"
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

with tempfile.TemporaryDirectory() as tmpdirname:
    options.add_argument(f'--user-data-dir={tmpdirname}')
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    print(driver.title)
    driver.quit()
