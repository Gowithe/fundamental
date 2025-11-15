import os
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

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
    """Safely call external API with error handling and logging"""
    try:
        print(f"[API CALL] {url} with params: {params}")
        response = requests.get(url, params=params, timeout=timeout)
        
        # Log response status
        print(f"[RESPONSE] Status: {response.status_code}")
        
        # Try to parse JSON
        try:
            data = response.json()
            print(f"[DATA] {json.dumps(data)[:200]}...")
            return data
        except:
            print(f"[ERROR] Could not parse JSON: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"[ERROR] API Timeout: {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection Error: {str(e)}")
        return None
    except Exception as e:
        print(f"[ERROR] API Error: {str(e)}")
        return None

def format_number(num):
    """Format numbers for display"""
    if num is None or num == 0:
        return "N/A"
    try:
        if abs(num) >= 1e9:
            return f"${num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.2f}M"
        else:
            return f"${num:,.2f}"
    except:
        return "N/A"

# =====================================================================
# HOME ROUTE (Main webpage)
# =====================================================================

@app.route('/')
def home():
    """Serve the main HTML page"""
    return render_template('index.html')

# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """
    Get current stock price and market data
    Returns: price, change%, open, high, low, volume
    """
    try:
        symbol = symbol.upper().strip()
        print(f"\n[PRICE] Fetching for: {symbol}")
        
        # Finnhub quote endpoint
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        data = safe_api_call(f"{FINNHUB_BASE_URL}/quote", params)
        
        if not data:
            print(f"[ERROR] No data returned for {symbol}")
            return jsonify({
                "error": "No data from API",
                "symbol": symbol,
                "data": None
            }), 500
        
        # Check if error in response
        if 'error' in data or 'c' not in data:
            print(f"[ERROR] API returned: {data}")
            return jsonify({
                "error": str(data.get('error', 'Unknown error')),
                "symbol": symbol,
                "data": None
            }), 400
        
        # Parse response
        current_price = data.get('c', 0)
        change = data.get('d', 0)
        change_percent = data.get('dp', 0)
        open_price = data.get('o', 0)
        high = data.get('h', 0)
        low = data.get('l', 0)
        
        result = {
            "symbol": symbol,
            "current_price": round(float(current_price), 2),
            "change": round(float(change), 2),
            "change_percent": round(float(change_percent), 2),
            "open": round(float(open_price), 2),
            "high": round(float(high), 2),
            "low": round(float(low), 2),
            "status": "success"
        }
        
        print(f"[SUCCESS] Price data: {result}")
        return jsonify(result)
    
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """
    Get latest company news (5-10 articles)
    """
    try:
        symbol = symbol.upper().strip()
        print(f"\n[NEWS] Fetching for: {symbol}")
        
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        data = safe_api_call(f"{FINNHUB_BASE_URL}/company-news", params)
        
        if not data:
            print(f"[ERROR] No news data for {symbol}")
            return jsonify({"error": "Could not fetch news", "news": []}), 500
        
        # Check if it's a list
        if not isinstance(data, list):
            print(f"[ERROR] News data is not a list: {data}")
            return jsonify({"error": "Invalid news format", "news": []}), 500
        
        # Process top 8 news items
        news_list = []
        for item in data[:8]:
            try:
                news_list.append({
                    "headline": item.get('headline', 'N/A'),
                    "summary": item.get('summary', 'N/A')[:200],
                    "source": item.get('source', 'Unknown'),
                    "url": item.get('url', '#'),
                    "datetime": item.get('datetime', 0),
                    "image": item.get('image', '')
                })
            except Exception as e:
                print(f"[ERROR] Processing news item: {str(e)}")
                continue
        
        result = {
            "symbol": symbol,
            "news": news_list,
            "status": "success"
        }
        
        print(f"[SUCCESS] Got {len(news_list)} news articles")
        return jsonify(result)
    
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/financials/<symbol>', methods=['GET'])
def get_financials(symbol):
    """
    Get financial metrics: revenue, net income, EPS, margins, ratios
    """
    try:
        symbol = symbol.upper().strip()
        print(f"\n[FINANCIALS] Fetching for: {symbol}")
        
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        # Get metrics from Finnhub
        data = safe_api_call(f"{FINNHUB_BASE_URL}/stock/metric", params)
        
        if not data:
            print(f"[ERROR] No financials data for {symbol}")
            return jsonify({"error": "Financial data not available", "data": None}), 500
        
        # Check for error or missing metric
        if 'error' in data:
            print(f"[ERROR] API returned: {data}")
            return jsonify({"error": str(data.get('error')), "data": None}), 400
        
        if 'metric' not in data:
            print(f"[WARNING] No metric in response: {list(data.keys())}")
            return jsonify({"error": "No metric data available", "data": None}), 400
        
        metric = data.get('metric', {})
        
        try:
            financials = {
                "symbol": symbol,
                "revenue_yoy_growth": round(float(metric.get('10Y Revenue Growth (per Share)', 0)), 2),
                "net_income_ttm": format_number(metric.get('Net Income', 0)),
                "eps_ttm": round(float(metric.get('Trailing Earnings Per Share', 0)), 2),
                "profit_margin": round(float(metric.get('Profit Margin', 0) or 0) * 100, 2),
                "gross_margin": round(float(metric.get('Gross Margin', 0) or 0) * 100, 2),
                "debt_to_equity": round(float(metric.get('Debt-to-Equity', 0)), 2),
                "free_cash_flow": format_number(metric.get('Free Cash Flow per Share', 0)),
                "pe_ratio": round(float(metric.get('P/E', 0)), 2),
                "forward_pe": round(float(metric.get('Forward P/E', 0)), 2),
                "peg_ratio": round(float(metric.get('PEG Ratio', 0)), 2),
                "ps_ratio": round(float(metric.get('Price-to-Sales', 0)), 2),
                "pb_ratio": round(float(metric.get('Price-to-Book', 0)), 2),
                "roe": round(float(metric.get('Return on Equity', 0) or 0) * 100, 2),
                "roa": round(float(metric.get('Return on Assets', 0) or 0) * 100, 2),
                "status": "success"
            }
        except Exception as e:
            print(f"[ERROR] Processing financials: {str(e)}")
            return jsonify({"error": f"Error processing data: {str(e)}", "data": None}), 500
        
        print(f"[SUCCESS] Financials data retrieved")
        return jsonify(financials)
    
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/overview/<symbol>', methods=['GET'])
def get_overview(symbol):
    """
    Get company overview: name, industry, market cap, CEO, etc.
    """
    try:
        symbol = symbol.upper().strip()
        print(f"\n[OVERVIEW] Fetching for: {symbol}")
        
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        data = safe_api_call(f"{FINNHUB_BASE_URL}/stock/profile2", params)
        
        if not data:
            print(f"[ERROR] No overview data for {symbol}")
            return jsonify({"error": "Company data not found", "data": None}), 500
        
        if 'error' in data or 'name' not in data:
            print(f"[ERROR] API returned: {data}")
            return jsonify({"error": "Company not found", "data": None}), 404
        
        overview = {
            "symbol": symbol,
            "company_name": data.get('name', 'N/A'),
            "industry": data.get('finnhubIndustry', 'N/A'),
            "website": data.get('weburl', 'N/A'),
            "market_cap": data.get('marketCapitalization', 0),
            "market_cap_formatted": format_number(float(data.get('marketCapitalization', 0)) * 1e6),
            "employees": data.get('employeeTotal', 0),
            "description": data.get('description', 'N/A')[:300],
            "ipo_date": data.get('ipo', 'N/A'),
            "status": "success"
        }
        
        print(f"[SUCCESS] Overview: {data.get('name')}")
        return jsonify(overview)
    
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/indicators/<symbol>', methods=['GET'])
def get_indicators(symbol):
    """
    Get technical indicators from Alpha Vantage (RSI, MACD)
    """
    try:
        symbol = symbol.upper().strip()
        print(f"\n[INDICATORS] Fetching for: {symbol}")
        
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
            try:
                latest_rsi = list(rsi_data['Technical Analysis: RSI'].values())[0]
                rsi_value = round(float(latest_rsi.get('RSI', 50)), 2)
                print(f"[SUCCESS] RSI: {rsi_value}")
            except Exception as e:
                print(f"[ERROR] Processing RSI: {str(e)}")
        else:
            print(f"[WARNING] No RSI data: {rsi_data}")
        
        if macd_data and 'Technical Analysis: MACD' in macd_data:
            try:
                latest_macd = list(macd_data['Technical Analysis: MACD'].values())[0]
                macd_value = round(float(latest_macd.get('MACD', 0)), 4)
                print(f"[SUCCESS] MACD: {macd_value}")
            except Exception as e:
                print(f"[ERROR] Processing MACD: {str(e)}")
        else:
            print(f"[WARNING] No MACD data: {macd_data}")
        
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
        print(f"[EXCEPTION] {str(e)}")
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/api/dummy', methods=['GET'])
def get_dummy():
    """
    Dummy endpoint for testing (no API calls)
    """
    print("\n[DUMMY] Test endpoint called")
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

# =====================================================================
# RUN APPLICATION
# =====================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"🚀 Stock Analyzer Starting on port {port}")
    print(f"{'='*60}\n")
    app.run(debug=False, host='0.0.0.0', port=port)
