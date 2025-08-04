from flask import Flask, request
from pybit.unified_trading import HTTP
import os

app = Flask(__name__)

# Use your API keys from Render environment (secure)
session = HTTP(
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET")
)

position_open = False

@app.route('/webhook', methods=['POST'])
def webhook():
    global position_open
    data = request.json

    if data.get("passphrase") != os.getenv("PASS"):
        return {"error": "Unauthorized"}, 401

    if position_open:
        return {"status": "Already in position"}

    # Get SOL price
    ticker = session.get_ticker(symbol="SOLUSDT")["result"]["list"][0]
    price = float(ticker["lastPrice"])

    qty = round((3 * 60) / price, 3)
    tp = round(price - 1, 2)
    sl = round(price + 2, 2)

    session.place_order(
        category="linear",
        symbol="SOLUSDT",
        side="Sell",
        order_type="Market",
        qty=qty,
        time_in_force="GoodTillCancel",
        take_profit=tp,
        stop_loss=sl,
        reduce_only=False
    )

    position_open = True
    return {"status": "Short placed"}

@app.route('/reset', methods=['POST'])
def reset():
    global position_open
    position_open = False
    return {"status": "Reset done"}

@app.route('/')
def home():
    return "Bot is running"
