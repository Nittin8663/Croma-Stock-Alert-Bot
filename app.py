from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

app = Flask(__name__)

def check_stock(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # You may need to specify the executable path if chromedriver is not in PATH
    # Example: webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    buy_now_btn = soup.find("button", class_="buyNowBtn")
    add_to_cart_btn = soup.find("button", class_="pdp-add-to-cart")

    if (buy_now_btn and "Buy Now" in buy_now_btn.text) or (add_to_cart_btn and "Add to Cart" in add_to_cart_btn.text):
        return "In Stock"
    else:
        return "Out of Stock"

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    product_url = None
    if request.method == 'POST':
        product_url = request.form.get('product_url')
        if product_url:
            status = check_stock(product_url)
    return render_template('index.html', status=status, product_url=product_url)

if __name__ == '__main__':
    app.run(debug=True)
