# main.py

import requests
from bs4 import BeautifulSoup
import telegram
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_env_variable(var_name):
    """
    Retrieves an environment variable. Raises an error if not found.
    """
    value = os.getenv(var_name)
    if not value:
        logging.error(f"Environment variable '{var_name}' not set.")
        raise ValueError(f"Environment variable '{var_name}' not set.")
    return value

def check_stock(product_url, in_stock_keywords):
    """
    Checks the stock status of a product on Croma's website.

    Args:
        product_url (str): The URL of the Croma product page.
        in_stock_keywords (list): A list of strings indicating "in stock" status.

    Returns:
        bool: True if the item is in stock, False otherwise.
        str: The current stock status text found on the page, or an error message.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        logging.info(f"Checking URL: {product_url}")
        response = requests.get(product_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Croma's stock status is often found in elements related to "Add to Cart" or specific status messages.
        # We'll look for common indicators. This might need adjustment if Croma's HTML changes.
        stock_status_element = soup.find(class_='pdp-add-to-cart') # Common class for add to cart button
        if not stock_status_element:
            # Fallback: search for common stock status texts in the entire body
            body_text = soup.body.get_text()
            for keyword in in_stock_keywords:
                if keyword.lower() in body_text.lower():
                    logging.info(f"Found keyword '{keyword}' in page text.")
                    return True, f"Status: '{keyword}' (found in body)"
            if "out of stock" in body_text.lower() or "currently unavailable" in body_text.lower():
                return False, "Status: Out of Stock (found in body)"
            return False, "Status: Not found (no specific element or keywords)"

        # Check text content of the found element for "Add to Cart" or similar
        status_text = stock_status_element.get_text(strip=True).lower()
        logging.info(f"Found potential stock status text: '{status_text}'")

        for keyword in in_stock_keywords:
            if keyword.lower() in status_text:
                return True, f"Status: '{keyword}'"

        if "out of stock" in status_text or "currently unavailable" in status_text:
            return False, "Status: Out of Stock"

        return False, f"Status: Unknown ('{status_text}')"

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return False, f"Error: Request failed - {e}"
    except Exception as e:
        logging.error(f"An unexpected error occurred during stock check: {e}")
        return False, f"Error: Unexpected error - {e}"

def send_telegram_message(bot_token, chat_id, message):
    """
    Sends a message to a Telegram chat.
    """
    try:
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message)
        logging.info(f"Telegram message sent successfully to chat ID {chat_id}.")
    except telegram.error.TelegramError as e:
        logging.error(f"Failed to send Telegram message: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending Telegram message: {e}")

def main():
    """
    Main function to run the Croma stock alert bot.
    """
    try:
        TELEGRAM_BOT_TOKEN = get_env_variable("TELEGRAM_BOT_TOKEN")
        TELEGRAM_CHAT_ID = get_env_variable("TELEGRAM_CHAT_ID")
        CROMA_PRODUCT_URL = get_env_variable("CROMA_PRODUCT_URL")
        # Keywords that indicate the item is in stock. Adjust as needed.
        IN_STOCK_KEYWORDS = ["add to cart", "buy now", "in stock", "available"]

        logging.info("Croma Stock Alert Bot started.")
        logging.info(f"Monitoring: {CROMA_PRODUCT_URL}")
        logging.info(f"Check interval: 20 seconds")

        last_known_in_stock_status = None # Use None to indicate initial unknown state

        while True:
            is_in_stock, status_text = check_stock(CROMA_PRODUCT_URL, IN_STOCK_KEYWORDS)

            if is_in_stock and last_known_in_stock_status is not True:
                message = f"🚨 Croma Stock Alert! 🚨\n\nItem is now IN STOCK!\nStatus: {status_text}\nLink: {CROMA_PRODUCT_URL}"
                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
                logging.info(f"Notification sent: Item is IN STOCK. {status_text}")
                last_known_in_stock_status = True
            elif not is_in_stock and last_known_in_stock_status is not False:
                message = f"Item is currently OUT OF STOCK.\nStatus: {status_text}\nLink: {CROMA_PRODUCT_URL}"
                # You might not want to send an "out of stock" notification every time it's checked,
                # but only when it changes from in-stock to out-of-stock.
                # For simplicity, we'll only notify on "in stock" change.
                logging.info(f"Item is OUT OF STOCK. {status_text}")
                last_known_in_stock_status = False
            else:
                logging.info(f"No change in stock status. Current status: {'IN STOCK' if is_in_stock else 'OUT OF STOCK'}. {status_text}")

            time.sleep(20) # Wait for 20 seconds before checking again

    except ValueError as ve:
        logging.critical(f"Configuration error: {ve}. Exiting.")
    except Exception as e:
        logging.critical(f"An unhandled error occurred: {e}. Bot will exit.")

if __name__ == "__main__":
    main()
