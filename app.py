import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return render_template('index.html')
# =====================================================================
# API KEYS (Never expose to frontend)
# =====================================================================
FINNHUB_API_KEY = "d46ntu1r01qgc9etnfngd46ntu1r01qgc9etnfo0"
ALPHA_VANTAGE_API_KEY = "SSHS1YDZEUU1VQM0"

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def safe_api_call(url, params, timeout=10):
    """Safely call external API with error handling"""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        return None

def format_number(num):
    """Format numbers for display"""
    if num is None:
        return "N/A"
    if abs(num) >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.2f}"

# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.route('/')
def home():
    return jsonify({"message": "Stock Analyzer API Running ✓"})

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """
    Get current stock price and market data
    Returns: price, change%, open, high, low, volume
    """
    try:
        symbol = symbol.upper()
        
        # Finnhub quote endpoint
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        data = safe_api_call(f"{FINNHUB_BASE_URL}/quote", params)
        
        if not data or 'c' not in data:
            return jsonify({
                "error": "Symbol not found",
                "symbol": symbol,
                "data": None
            }), 404
        
        # Parse response
        current_price = data.get('c', 0)
        change = data.get('d', 0)
        change_percent = data.get('dp', 0)
        open_price = data.get('o', 0)
        high = data.get('h', 0)
        low = data.get('l', 0)
        
        return jsonify({
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """
    Get latest company news (5-10 articles)
    """
    try:
        symbol = symbol.upper()
        
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        data = safe_api_call(f"{FINNHUB_BASE_URL}/company-news", params)
        
        if not data:
            return jsonify({"error": "Could not fetch news", "news": []}), 500
        
        # Process top 8 news items
        news_list = []
        for item in data[:8]:
            news_list.append({
                "headline": item.get('headline', 'N/A'),
                "summary": item.get('summary', 'N/A')[:200],
                "source": item.get('source', 'Unknown'),
                "url": item.get('url', '#'),
                "datetime": item.get('datetime', 0),
                "image": item.get('image', '')
            })
        
        return jsonify({
            "symbol": symbol,
            "news": news_list,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/financials/<symbol>', methods=['GET'])
def get_financials(symbol):
    """
    Get financial metrics: revenue, net income, EPS, margins, ratios
    """
    try:
        symbol = symbol.upper()
        
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        # Get metrics from Finnhub
        data = safe_api_call(f"{FINNHUB_BASE_URL}/stock/metric", params)
        
        if not data or 'metric' not in data:
            return jsonify({"error": "Financial data not available", "data": None}), 404
        
        metric = data.get('metric', {})
        
        financials = {
            "symbol": symbol,
            "revenue_yoy_growth": round(metric.get('10Y Revenue Growth (per Share)', 0), 2),
            "net_income_ttm": format_number(metric.get('Net Income', 0)),
            "eps_ttm": round(metric.get('Trailing Earnings Per Share', 0), 2),
            "profit_margin": round(metric.get('Profit Margin', 0) * 100, 2),
            "gross_margin": round(metric.get('Gross Margin', 0) * 100, 2),
            "debt_to_equity": round(metric.get('Debt-to-Equity', 0), 2),
            "free_cash_flow": format_number(metric.get('Free Cash Flow per Share', 0)),
            "pe_ratio": round(metric.get('P/E', 0), 2),
            "forward_pe": round(metric.get('Forward P/E', 0), 2),
            "peg_ratio": round(metric.get('PEG Ratio', 0), 2),
            "ps_ratio": round(metric.get('Price-to-Sales', 0), 2),
            "pb_ratio": round(metric.get('Price-to-Book', 0), 2),
            "roe": round(metric.get('Return on Equity', 0) * 100, 2),
            "roa": round(metric.get('Return on Assets', 0) * 100, 2),
            "status": "success"
        }
        
        return jsonify(financials)
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/overview/<symbol>', methods=['GET'])
def get_overview(symbol):
    """
    Get company overview: name, industry, market cap, CEO, etc.
    """
    try:
        symbol = symbol.upper()
        
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        data = safe_api_call(f"{FINNHUB_BASE_URL}/stock/profile2", params)
        
        if not data or 'name' not in data:
            return jsonify({"error": "Company data not found", "data": None}), 404
        
        overview = {
            "symbol": symbol,
            "company_name": data.get('name', 'N/A'),
            "industry": data.get('finnhubIndustry', 'N/A'),
            "website": data.get('weburl', 'N/A'),
            "market_cap": data.get('marketCapitalization', 0),
            "market_cap_formatted": format_number(data.get('marketCapitalization', 0) * 1e6),
            "employees": data.get('employeeTotal', 0),
            "description": data.get('description', 'N/A')[:300],
            "ipo_date": data.get('ipo', 'N/A'),
            "status": "success"
        }
        
        return jsonify(overview)
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/indicators/<symbol>', methods=['GET'])
def get_indicators(symbol):
    """
    Get technical indicators from Alpha Vantage (RSI, MACD)
    """
    try:
        symbol = symbol.upper()
        
        # Get RSI
        params_rsi = {
            'function': 'RSI',
            'symbol': symbol,
            'interval': 'daily',
            'time_period': 14,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        rsi_data = safe_api_call(ALPHA_VANTAGE_BASE_URL, params_rsi)
        
        # Get MACD
        params_macd = {
            'function': 'MACD',
            'symbol': symbol,
            'interval': 'daily',
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        macd_data = safe_api_call(ALPHA_VANTAGE_BASE_URL, params_macd)
        
        # Extract latest values
        rsi_value = 50  # Default neutral
        macd_value = 0  # Default neutral
        
        if rsi_data and 'Technical Analysis: RSI' in rsi_data:
            latest_rsi = list(rsi_data['Technical Analysis: RSI'].values())[0]
            rsi_value = round(float(latest_rsi.get('RSI', 50)), 2)
        
        if macd_data and 'Technical Analysis: MACD' in macd_data:
            latest_macd = list(macd_data['Technical Analysis: MACD'].values())[0]
            macd_value = round(float(latest_macd.get('MACD', 0)), 4)
        
        indicators = {
            "symbol": symbol,
            "rsi": rsi_value,
            "rsi_signal": "Overbought" if rsi_value > 70 else "Oversold" if rsi_value < 30 else "Neutral",
            "macd": macd_value,
            "macd_signal": "Bullish" if macd_value > 0 else "Bearish",
            "status": "success"
        }
        
        return jsonify(indicators)
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/dummy', methods=['GET'])
def get_dummy():
    """
    Dummy endpoint for testing (no API calls)
    """
    return jsonify({
        "symbol": "AAPL",
        "current_price": 235.75,
        "change": 2.50,
        "change_percent": 1.07,
        "company_name": "Apple Inc.",
        "industry": "Technology",
        "market_cap_formatted": "$2.8T",
        "pe_ratio": 28.5,
        "profit_margin": 25.3,
        "status": "success"
    })

# =====================================================================
# ERROR HANDLERS
# =====================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": "failed"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
