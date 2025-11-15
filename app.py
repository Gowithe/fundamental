from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

# โหลด environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'd46ntu1r01qgc9etnfngd46ntu1r01qgc9etnfo0')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'SSHS1YDZEUU1VQM0')

# Cache dictionary
cache = {}
CACHE_DURATION = 300  # 5 นาที

# Rate limiting
last_alpha_call = 0
ALPHA_RATE_LIMIT = 12  # 12 วินาที ระหว่างแต่ละ call (5 calls/minute)

def get_cached_data(key, fetch_function, *args, **kwargs):
    """ดึงข้อมูลจาก cache หรือเรียก API ใหม่ถ้าหมดอายุ"""
    now = time.time()
    
    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < CACHE_DURATION:
            print(f"[CACHE HIT] {key}")
            return data
    
    print(f"[CACHE MISS] {key} - Fetching new data...")
    data = fetch_function(*args, **kwargs)
    cache[key] = (data, now)
    return data

def alpha_vantage_call_with_limit(url, params):
    """เรียก Alpha Vantage API พร้อมจัดการ rate limit"""
    global last_alpha_call
    
    now = time.time()
    time_since_last = now - last_alpha_call
    
    if time_since_last < ALPHA_RATE_LIMIT:
        wait_time = ALPHA_RATE_LIMIT - time_since_last
        print(f"[RATE LIMIT] Waiting {wait_time:.1f} seconds...")
        time.sleep(wait_time)
    
    try:
        response = requests.get(url, params=params, timeout=10)
        last_alpha_call = time.time()
        
        if response.status_code == 200:
            data = response.json()
            
            # ตรวจสอบ rate limit message
            if 'Note' in data:
                print(f"[ALPHA WARNING] {data['Note']}")
                return {'error': 'Rate limit reached. Please try again later.'}
            
            # ตรวจสอบ premium message
            if 'Information' in data:
                print(f"[ALPHA INFO] {data['Information']}")
                return {'error': 'API limit reached. Using cached data when available.'}
            
            return data
        else:
            print(f"[ALPHA ERROR] Status {response.status_code}")
            return {'error': f'API returned status {response.status_code}'}
            
    except Exception as e:
        print(f"[ALPHA ERROR] {str(e)}")
        return {'error': str(e)}

@app.route('/')
def index():
    """หน้าหลัก"""
    return render_template('index.html')

@app.route('/api/price/<symbol>')
def get_price(symbol):
    """ดึงราคาหุ้นปัจจุบัน"""
    def fetch_price():
        try:
            url = 'https://finnhub.io/api/v1/quote'
            params = {'symbol': symbol.upper(), 'token': FINNHUB_API_KEY}
            
            print(f"[PRICE] Fetching for: {symbol}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol.upper(),
                    'current': data.get('c', 0),
                    'change': data.get('d', 0),
                    'percent': data.get('dp', 0),
                    'high': data.get('h', 0),
                    'low': data.get('l', 0),
                    'open': data.get('o', 0),
                    'previous_close': data.get('pc', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"[PRICE ERROR] Status {response.status_code}")
                return {'error': 'Failed to fetch price data'}
                
        except Exception as e:
            print(f"[PRICE ERROR] {str(e)}")
            return {'error': str(e)}
    
    cache_key = f'price_{symbol}'
    return jsonify(get_cached_data(cache_key, fetch_price))

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """ดึงข่าวบริษัท - แก้ไข date format"""
    def fetch_news():
        try:
            url = 'https://finnhub.io/api/v1/company-news'
            
            # ✅ แก้ไข: ใช้ date format YYYY-MM-DD
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            params = {
                'symbol': symbol.upper(),
                'from': from_date,
                'to': to_date,
                'token': FINNHUB_API_KEY
            }
            
            print(f"[NEWS] Fetching for: {symbol}")
            print(f"[API CALL] {url} with params: {{'symbol': '{symbol}', 'token': '{FINNHUB_API_KEY[:10]}...'}}")
            
            response = requests.get(url, params=params, timeout=10)
            print(f"[RESPONSE] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # ตรวจสอบว่าข้อมูลเป็น list หรือ dict (error)
                if isinstance(data, dict):
                    if 'error' in data:
                        print(f"[ERROR] News data is not a list: {data}")
                        return {'error': data.get('error'), 'articles': []}
                    return {'articles': []}
                
                # ตัดให้เหลือแค่ 10 ข่าวล่าสุด
                articles = data[:10] if isinstance(data, list) else []
                
                formatted_news = []
                for article in articles:
                    formatted_news.append({
                        'headline': article.get('headline', 'No headline'),
                        'summary': article.get('summary', 'No summary available'),
                        'source': article.get('source', 'Unknown'),
                        'url': article.get('url', '#'),
                        'datetime': article.get('datetime', 0),
                        'image': article.get('image', '')
                    })
                
                print(f"[DATA] {len(formatted_news)} articles found")
                return {'articles': formatted_news}
            else:
                print(f"[NEWS ERROR] Status {response.status_code}")
                return {'error': f'API returned status {response.status_code}', 'articles': []}
                
        except Exception as e:
            print(f"[NEWS ERROR] {str(e)}")
            return {'error': str(e), 'articles': []}
    
    cache_key = f'news_{symbol}'
    return jsonify(get_cached_data(cache_key, fetch_news))

@app.route('/api/overview/<symbol>')
def get_overview(symbol):
    """ดึงข้อมูลภาพรวมบริษัท"""
    def fetch_overview():
        try:
            url = 'https://finnhub.io/api/v1/stock/profile2'
            params = {'symbol': symbol.upper(), 'token': FINNHUB_API_KEY}
            
            print(f"[OVERVIEW] Fetching for: {symbol}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', 'N/A'),
                    'ticker': data.get('ticker', symbol.upper()),
                    'exchange': data.get('exchange', 'N/A'),
                    'industry': data.get('finnhubIndustry', 'N/A'),
                    'market_cap': data.get('marketCapitalization', 0),
                    'country': data.get('country', 'N/A'),
                    'currency': data.get('currency', 'USD'),
                    'ipo': data.get('ipo', 'N/A'),
                    'logo': data.get('logo', ''),
                    'weburl': data.get('weburl', '#')
                }
            else:
                print(f"[OVERVIEW ERROR] Status {response.status_code}")
                return {'error': 'Failed to fetch company overview'}
                
        except Exception as e:
            print(f"[OVERVIEW ERROR] {str(e)}")
            return {'error': str(e)}
    
    cache_key = f'overview_{symbol}'
    return jsonify(get_cached_data(cache_key, fetch_overview))

@app.route('/api/financials/<symbol>')
def get_financials(symbol):
    """ดึงข้อมูลทางการเงิน"""
    def fetch_financials():
        try:
            # ดึงข้อมูลพื้นฐานจาก Finnhub
            url = 'https://finnhub.io/api/v1/stock/metric'
            params = {
                'symbol': symbol.upper(),
                'metric': 'all',
                'token': FINNHUB_API_KEY
            }
            
            print(f"[FINANCIALS] Fetching for: {symbol}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metric', {})
                
                return {
                    'revenue_ttm': metrics.get('revenueTTM', 0),
                    'revenue_growth': metrics.get('revenueGrowthTTMYoy', 0),
                    'net_income': metrics.get('netIncomeTTM', 0),
                    'eps': metrics.get('epsTTM', 0),
                    'eps_growth': metrics.get('epsGrowthTTMYoy', 0),
                    'profit_margin': metrics.get('netProfitMarginTTM', 0),
                    'operating_margin': metrics.get('operatingMarginTTM', 0),
                    'debt_equity': metrics.get('totalDebt/totalEquityQuarterly', 0),
                    'current_ratio': metrics.get('currentRatioQuarterly', 0),
                    'pe_ratio': metrics.get('peBasicExclExtraTTM', 0),
                    'pb_ratio': metrics.get('pbQuarterly', 0),
                    'ps_ratio': metrics.get('psTTM', 0),
                    'peg_ratio': metrics.get('pegRatio', 0),
                    'roe': metrics.get('roeTTM', 0),
                    'roa': metrics.get('roaTTM', 0),
                    'free_cash_flow': metrics.get('freeCashFlowTTM', 0),
                    'beta': metrics.get('beta', 0),
                    '52_week_high': metrics.get('52WeekHigh', 0),
                    '52_week_low': metrics.get('52WeekLow', 0)
                }
            else:
                print(f"[FINANCIALS ERROR] Status {response.status_code}")
                return {'error': 'Failed to fetch financial data'}
                
        except Exception as e:
            print(f"[FINANCIALS ERROR] {str(e)}")
            return {'error': str(e)}
    
    cache_key = f'financials_{symbol}'
    return jsonify(get_cached_data(cache_key, fetch_financials))

@app.route('/api/indicators/<symbol>')
def get_indicators(symbol):
    """ดึง Technical Indicators จาก Alpha Vantage พร้อม rate limiting"""
    def fetch_indicators():
        try:
            indicators = {}
            
            # RSI
            print(f"[INDICATORS] Fetching RSI for: {symbol}")
            rsi_url = 'https://www.alphavantage.co/query'
            rsi_params = {
                'function': 'RSI',
                'symbol': symbol.upper(),
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close',
                'apikey': ALPHA_VANTAGE_API_KEY
            }
            
            rsi_data = alpha_vantage_call_with_limit(rsi_url, rsi_params)
            
            if 'error' not in rsi_data and 'Technical Analysis: RSI' in rsi_data:
                latest_rsi = list(rsi_data['Technical Analysis: RSI'].values())[0]
                indicators['rsi'] = float(latest_rsi.get('RSI', 0))
            else:
                indicators['rsi'] = None
                if 'error' in rsi_data:
                    print(f"[RSI ERROR] {rsi_data['error']}")
            
            # MACD
            print(f"[INDICATORS] Fetching MACD for: {symbol}")
            macd_url = 'https://www.alphavantage.co/query'
            macd_params = {
                'function': 'MACD',
                'symbol': symbol.upper(),
                'interval': 'daily',
                'series_type': 'close',
                'apikey': ALPHA_VANTAGE_API_KEY
            }
            
            macd_data = alpha_vantage_call_with_limit(macd_url, macd_params)
            
            if 'error' not in macd_data and 'Technical Analysis: MACD' in macd_data:
                latest_macd = list(macd_data['Technical Analysis: MACD'].values())[0]
                indicators['macd'] = {
                    'macd': float(latest_macd.get('MACD', 0)),
                    'signal': float(latest_macd.get('MACD_Signal', 0)),
                    'histogram': float(latest_macd.get('MACD_Hist', 0))
                }
            else:
                indicators['macd'] = None
                if 'error' in macd_data:
                    print(f"[MACD ERROR] {macd_data['error']}")
            
            return indicators
            
        except Exception as e:
            print(f"[INDICATORS ERROR] {str(e)}")
            return {'error': str(e)}
    
    cache_key = f'indicators_{symbol}'
    return jsonify(get_cached_data(cache_key, fetch_indicators))

@app.route('/api/health/<symbol>')
def get_health_score(symbol):
    """คำนวณคะแนนสุขภาพการเงิน"""
    def calculate_health():
        try:
            # ดึงข้อมูลทางการเงิน
            financials_response = get_financials(symbol)
            financials = financials_response.get_json()
            
            if 'error' in financials:
                return {'error': 'Cannot calculate health score'}
            
            score = 0
            max_score = 100
            factors = []
            
            # 1. กำไร (20 คะแนน)
            profit_margin = financials.get('profit_margin', 0)
            if profit_margin > 20:
                score += 20
                factors.append({'name': 'Profit Margin', 'score': 20, 'status': 'excellent'})
            elif profit_margin > 10:
                score += 15
                factors.append({'name': 'Profit Margin', 'score': 15, 'status': 'good'})
            elif profit_margin > 5:
                score += 10
                factors.append({'name': 'Profit Margin', 'score': 10, 'status': 'fair'})
            else:
                factors.append({'name': 'Profit Margin', 'score': 0, 'status': 'poor'})
            
            # 2. การเติบโตของรายได้ (15 คะแนน)
            revenue_growth = financials.get('revenue_growth', 0)
            if revenue_growth > 15:
                score += 15
                factors.append({'name': 'Revenue Growth', 'score': 15, 'status': 'excellent'})
            elif revenue_growth > 10:
                score += 12
                factors.append({'name': 'Revenue Growth', 'score': 12, 'status': 'good'})
            elif revenue_growth > 5:
                score += 8
                factors.append({'name': 'Revenue Growth', 'score': 8, 'status': 'fair'})
            else:
                factors.append({'name': 'Revenue Growth', 'score': 0, 'status': 'poor'})
            
            # 3. หนี้สิน (15 คะแนน)
            debt_equity = financials.get('debt_equity', 0)
            if debt_equity < 0.5:
                score += 15
                factors.append({'name': 'Debt Level', 'score': 15, 'status': 'excellent'})
            elif debt_equity < 1:
                score += 12
                factors.append({'name': 'Debt Level', 'score': 12, 'status': 'good'})
            elif debt_equity < 2:
                score += 8
                factors.append({'name': 'Debt Level', 'score': 8, 'status': 'fair'})
            else:
                factors.append({'name': 'Debt Level', 'score': 0, 'status': 'poor'})
            
            # 4. ROE (15 คะแนน)
            roe = financials.get('roe', 0)
            if roe > 15:
                score += 15
                factors.append({'name': 'ROE', 'score': 15, 'status': 'excellent'})
            elif roe > 10:
                score += 12
                factors.append({'name': 'ROE', 'score': 12, 'status': 'good'})
            elif roe > 5:
                score += 8
                factors.append({'name': 'ROE', 'score': 8, 'status': 'fair'})
            else:
                factors.append({'name': 'ROE', 'score': 0, 'status': 'poor'})
            
            # 5. P/E Ratio (15 คะแนน)
            pe_ratio = financials.get('pe_ratio', 0)
            if 10 < pe_ratio < 25:
                score += 15
                factors.append({'name': 'P/E Ratio', 'score': 15, 'status': 'excellent'})
            elif 5 < pe_ratio < 35:
                score += 10
                factors.append({'name': 'P/E Ratio', 'score': 10, 'status': 'good'})
            elif pe_ratio > 0:
                score += 5
                factors.append({'name': 'P/E Ratio', 'score': 5, 'status': 'fair'})
            else:
                factors.append({'name': 'P/E Ratio', 'score': 0, 'status': 'poor'})
            
            # 6. Current Ratio (10 คะแนน)
            current_ratio = financials.get('current_ratio', 0)
            if current_ratio > 2:
                score += 10
                factors.append({'name': 'Liquidity', 'score': 10, 'status': 'excellent'})
            elif current_ratio > 1.5:
                score += 8
                factors.append({'name': 'Liquidity', 'score': 8, 'status': 'good'})
            elif current_ratio > 1:
                score += 5
                factors.append({'name': 'Liquidity', 'score': 5, 'status': 'fair'})
            else:
                factors.append({'name': 'Liquidity', 'score': 0, 'status': 'poor'})
            
            # 7. Free Cash Flow (10 คะแนน)
            fcf = financials.get('free_cash_flow', 0)
            if fcf > 1000000000:  # > 1B
                score += 10
                factors.append({'name': 'Free Cash Flow', 'score': 10, 'status': 'excellent'})
            elif fcf > 0:
                score += 5
                factors.append({'name': 'Free Cash Flow', 'score': 5, 'status': 'good'})
            else:
                factors.append({'name': 'Free Cash Flow', 'score': 0, 'status': 'poor'})
            
            # กำหนดระดับ
            if score >= 80:
                rating = 'STRONG BUY'
                rating_class = 'excellent'
            elif score >= 65:
                rating = 'BUY'
                rating_class = 'good'
            elif score >= 50:
                rating = 'HOLD'
                rating_class = 'fair'
            elif score >= 35:
                rating = 'SELL'
                rating_class = 'warning'
            else:
                rating = 'STRONG SELL'
                rating_class = 'poor'
            
            return {
                'score': score,
                'max_score': max_score,
                'percentage': round((score / max_score) * 100, 1),
                'rating': rating,
                'rating_class': rating_class,
                'factors': factors
            }
            
        except Exception as e:
            print(f"[HEALTH ERROR] {str(e)}")
            return {'error': str(e)}
    
    cache_key = f'health_{symbol}'
    return jsonify(get_cached_data(cache_key, calculate_health))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
