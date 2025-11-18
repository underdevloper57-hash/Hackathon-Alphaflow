import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import stock_engine

# --- VERCEL PATH FIX ---
# This tells Flask exactly where to look for the templates folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# --- PAGE ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --- API ROUTES ---
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        ticker = data.get('ticker', 'TCS')
        result = stock_engine.analyze_ticker(ticker)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Ticker not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/market_status', methods=['GET'])
def market_status():
    try:
        result = stock_engine.analyze_ticker('^NSEI')
        if result:
            result['ticker'] = "NIFTY 50"
            return jsonify(result)
        return jsonify({"error": "Market data unavailable"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        msg = request.json.get('message', '')
        return jsonify({"response": stock_engine.get_chat_response(msg)})
    except Exception as e:
         return jsonify({"response": "AI Error: " + str(e)})

# Vercel requires the 'app' object to be available at the module level
if __name__ == '__main__':
    app.run(debug=True, port=5000)
