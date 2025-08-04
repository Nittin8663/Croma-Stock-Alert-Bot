from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def check_stock(url):
    import requests
    from bs4 import BeautifulSoup

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the Buy Now button by its class
    buy_now_btn = soup.find("button", class_="buyNowBtn")
    if buy_now_btn and "Buy Now" in buy_now_btn.text:
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
