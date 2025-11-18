import yfinance as yf
import pandas as pd
import numpy as np
import random

def get_data(ticker):
    try:
        if ticker == "NIFTY": ticker = "^NSEI"
        if not ticker.startswith('^') and '.' not in ticker and 'BTC' not in ticker and 'USD' not in ticker:
            ticker += ".NS"
            
        # Use Ticker object to avoid 403 Forbidden errors
        stock = yf.Ticker(ticker)
        data = stock.history(period="6mo", interval="1d")
        
        if data.empty: return None
        
        data.reset_index(inplace=True)
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_ticker(ticker):
    df = get_data(ticker)
    if df is None: return None
    
    current_price = float(df['Close'].iloc[-1])
    
    # 1. Format History for Candlestick Chart (x: Date, y: [O, H, L, C])
    history = []
    subset = df.tail(60)
    for _, row in subset.iterrows():
        date_str = str(row['Date']).split(' ')[0]
        history.append({
            "x": date_str,
            "y": [round(row['Open'], 2), round(row['High'], 2), round(row['Low'], 2), round(row['Close'], 2)]
        })
    
    # 2. Technicals
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    trend = 1 if current_price > df['Close'].iloc[-20] else -1
    volatility = df['Close'].pct_change().std() * 100

    # 3. AI Predictions (Simulated for Demo)
    # Gap logic
    gap_sentiment = random.uniform(-0.005, 0.008) * trend
    pred_open = current_price * (1 + gap_sentiment)

    # Models logic
    lstm_move = random.uniform(0.005, 0.02) * trend
    xgb_move = random.uniform(0.002, 0.012) * trend
    
    lstm_target = current_price * (1 + lstm_move)
    xgb_target = current_price * (1 + xgb_move)
    
    # Ensemble
    pred_close = (lstm_target * 0.6) + (xgb_target * 0.4)
    
    sent_score = random.uniform(0.4, 0.9) if trend == 1 else random.uniform(-0.8, -0.2)
    
    return {
        "ticker": ticker.upper(),
        "current_price": current_price,
        "history": history,
        "technicals": {
            "rsi": round(rsi, 1),
            "volatility": "High" if volatility > 1.5 else "Low"
        },
        "prediction": {
            "open": round(pred_open, 2),
            "close": round(pred_close, 2),
            "lstm": round(lstm_target, 2),     # REQUIRED FOR DASHBOARD
            "xgboost": round(xgb_target, 2)    # REQUIRED FOR DASHBOARD
        },
        "sentiment": {
            "score": round(sent_score, 2),
            "label": "Bullish" if sent_score > 0 else "Bearish"
        },
        "signal": "BUY" if pred_close > current_price else "SELL"
    }

def get_chat_response(user_msg):
    msg = user_msg.lower()
    if "rsi" in msg: return "RSI (Relative Strength Index) measures momentum. >70 is Overbought, <30 is Oversold."
    if "bullish" in msg: return "Bullish means prices are expected to rise."
    if "bearish" in msg: return "Bearish means prices are expected to fall."
    if "lstm" in msg: return "LSTM is a neural network that learns time-based patterns in stock prices."
    if "hello" in msg: return "Hello! I am AlphaBot. Ask me about stocks or technical terms."
    return "I am an AI assistant. I can explain market terms like RSI, MACD, or Bullish trends."
