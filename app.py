from flask import Flask, request, render_template, redirect, url_for
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def check_stock(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Check for the "Buy Now" button to determine if in stock
    buy_now_btn = soup.find("button", class_="buyNowBtn")
    if buy_now_btn:
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

# Example template: templates/index.html
# <form method="post">
#   <input name="product_url" placeholder="Paste Croma product URL">
#   <button type="submit">Watch Product</button>
# </form>
# {% if status %}
#   <p>Status: {{ status }}</p>
# {% endif %}

if __name__ == '__main__':
    app.run(debug=True)
