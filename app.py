from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def check_stock(url):
    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try Buy Now and Add to Cart (detect both)
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
