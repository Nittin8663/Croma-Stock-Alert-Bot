from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

def check_stock(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        # Wait up to 10 seconds for the Buy Now button to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "buyNowBtn"))
        )
    except Exception:
        pass  # It's okay if it times out

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    buy_now_btn = soup.find("button", class_="buyNowBtn")
    add_to_cart_btn = soup.find("button", class_="pdp-add-to-cart")

    if (buy_now_btn and "Buy Now" in buy_now_btn.text) or (add_to_cart_btn and "Add to Cart" in add_to_cart_btn.text):
        return "In Stock"
    else:
        return "Out of Stock"

@app.route("/", methods=["GET", "POST"])
def index():
    status = None
    product_url = None
    if request.method == "POST":
        product_url = request.form.get("product_url")
        if product_url:
            status = check_stock(product_url)
    return render_template("index.html", status=status, product_url=product_url)

if __name__ == "__main__":
    app.run(debug=True)
