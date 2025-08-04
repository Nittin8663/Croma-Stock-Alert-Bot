import os
import threading
import time
from flask import Flask, request, render_template_string
from stock_checker import is_in_stock
from telegram_notifier import send_telegram_message

# Load environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

app = Flask(__name__)

WATCHED_PRODUCTS = []  # List of dicts: {'url': ..., 'in_stock': False}

HTML_TEMPLATE = open("index.html").read()

@app.route("/", methods=["GET", "POST"])
def index():
    global WATCHED_PRODUCTS
    if request.method == "POST":
        url = request.form["url"].strip()
        if url and not any(p['url'] == url for p in WATCHED_PRODUCTS):
            WATCHED_PRODUCTS.append({'url': url, 'in_stock': False})
    return render_template_string(HTML_TEMPLATE, products=WATCHED_PRODUCTS)

def background_stock_check():
    while True:
        for product in WATCHED_PRODUCTS:
            try:
                in_stock = is_in_stock(product['url'])
                if in_stock and not product['in_stock']:
                    send_telegram_message(BOT_TOKEN, CHAT_ID, f"Croma Stock Alert 🚨\nProduct is back in stock!\n{product['url']}")
                product['in_stock'] = in_stock
            except Exception as e:
                print(f"Error checking {product['url']}: {e}")
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    threading.Thread(target=background_stock_check, daemon=True).start()
    app.run(debug=True)
