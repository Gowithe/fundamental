import os
from datetime import datetime
import logging

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests

# -----------------------
# Config basic app
# -----------------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------
# API Keys (ใช้ ENV เท่านั้น)
# -----------------------
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if not FINNHUB_API_KEY:
    logger.warning("FINNHUB_API_KEY is not set. Some endpoints may fail.")
if not ALPHA_VANTAGE_API_KEY:
    logger.warning("ALPHA_VANTAGE_API_KEY is not set. Indicators endpoint may fail.")

FINNHUB_BASE = "https://finnhub.io/api/v1"
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"

# Simple in-memory cache
cache = {}
CACHE_TTL_SEC = 300  # 5 นาที


def cache_get(key: str):
    entry = cache.get(key)
    if not entry:
        return None
    data, ts = entry
    if (datetime.now() - ts).seconds > CACHE_TTL_SEC:
        cache.pop(key, None)
        return None
    return data


def cache_set(key: str, value):
    cache[key] = (value, datetime.now())


# -----------------------
# Routes
# -----------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/price/<symbol>", methods=["GET"])
def api_price(symbol):
    """ราคาปัจจุบัน + เปลี่ยนแปลง %"""
    symbol = symbol.upper()
    cache_key = f"price_{symbol}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        url = f"{FINNHUB_BASE}/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        if not data or "c" not in data:
            return jsonify({"error": "Symbol not found"}), 404

        result = {
            "symbol": symbol,
            "current_price": round(data.get("c", 0), 2),
            "change": round(data.get("d", 0), 2),
            "change_percent": round(data.get("dp", 0), 2),
            "open": round(data.get("o", 0), 2),
            "high": round(data.get("h", 0), 2),
            "low": round(data.get("l", 0), 2),
            "previous_close": round(data.get("pc", 0), 2),
            "timestamp": datetime.now().isoformat()
        }
        cache_set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Price API error: {e}")
        return jsonify({"error": "Failed to fetch price data"}), 500


@app.route("/api/overview/<symbol>", methods=["GET"])
def api_overview(symbol):
    """ข้อมูลบริษัทพื้นฐาน"""
    symbol = symbol.upper()
    cache_key = f"overview_{symbol}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        url = f"{FINNHUB_BASE}/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        if not data:
            return jsonify({"error": "Company not found"}), 404

        result = {
            "symbol": symbol,
            "name": data.get("name", "N/A"),
            "industry": data.get("finnhubIndustry", "N/A"),
            "market_cap": data.get("marketCapitalization", 0),
            "country": data.get("country", "N/A"),
            "currency": data.get("currency", "USD"),
            "phone": data.get("phone", "N/A"),
            "website": data.get("weburl", "N/A"),
            "employees": data.get("employees", "N/A"),
            "ipo_date": data.get("ipo", "N/A"),
            "description": data.get("description", "N/A"),
            "logo": data.get("logo", "")
        }
        cache_set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Overview API error: {e}")
        return jsonify({"error": "Failed to fetch company overview"}), 500


@app.route("/api/financials/<symbol>", methods=["GET"])
def api_financials(symbol):
    """ตัวชี้วัดทางการเงินหลัก ๆ"""
    symbol = symbol.upper()
    cache_key = f"financials_{symbol}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        url = f"{FINNHUB_BASE}/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        if not data or "metric" not in data:
            return jsonify({"error": "Financial data not available"}), 404

        m = data["metric"]

        result = {
            "symbol": symbol,
            # Valuation
            "pe_ratio": round(m.get("peNormalizedAnnual", 0), 2),
            "forward_pe": round(m.get("peForward", 0), 2),
            "peg_ratio": round(m.get("pegNormalizedAnnual", 0), 2),
            "price_to_sales": round(m.get("psSimple", 0), 2),
            "price_to_book": round(m.get("pbAnnual", 0), 2),
            # Growth
            "earnings_per_share": round(m.get("epsAnnualized", 0), 2),
            "eps_growth_5y": round(m.get("epsGrowth5Y", 0), 2),
            "revenue_growth_5y": round(m.get("revenueGrowth5Y", 0), 2),
            # Margins
            "profit_margin": round(m.get("marginNet", 0), 2),
            "operating_margin": round(m.get("marginOperating", 0), 2),
            "gross_margin": round(m.get("marginGross", 0), 2),
            # Balance Sheet / Liquidity
            "debt_to_equity": round(m.get("debtToEquityAnnual", 0), 2),
            "debt_to_assets": round(m.get("debtToAssetsAnnual", 0), 2),
            "current_ratio": round(m.get("currentRatio", 0), 2),
            "quick_ratio": round(m.get("quickRatio", 0), 2),
            # Cash Flow
            "free_cash_flow": round(m.get("fcfAnnual", 0), 2),
            "free_cash_flow_per_share": round(m.get("fcfPerShareAnnual", 0), 2),
            # Returns
            "dividend_yield": round(m.get("dividendYieldIndicatedAnnual", 0), 4),
            "return_on_equity": round(m.get("roeAnnual", 0), 2),
            "return_on_assets": round(m.get("roaAnnual", 0), 2),
        }
        cache_set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Financials API error: {e}")
        return jsonify({"error": "Failed to fetch financial data"}), 500


@app.route("/api/news/<symbol>", methods=["GET"])
def api_news(symbol):
    """ข่าวบริษัท 10 ข่าวล่าสุด"""
    symbol = symbol.upper()
    cache_key = f"news_{symbol}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        # last 7 days
        to_date = datetime.utcnow().date()
        from_date = to_date.replace(day=max(1, to_date.day - 7))

        url = (
            f"{FINNHUB_BASE}/company-news?symbol={symbol}"
            f"&from={from_date.isoformat()}&to={to_date.isoformat()}"
            f"&token={FINNHUB_API_KEY}"
        )
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        news_list = r.json() or []

        articles = []
        for item in news_list[:10]:
            articles.append({
                "headline": item.get("headline", "N/A"),
                "summary": item.get("summary", "")[:220],
                "source": item.get("source", "Unknown"),
                "url": item.get("url", ""),
                "image": item.get("image", ""),
                "datetime": item.get("datetime", 0),
            })

        result = {"symbol": symbol, "news": articles}
        cache_set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"News API error: {e}")
        return jsonify({"symbol": symbol, "news": []})


@app.route("/api/indicators/<symbol>", methods=["GET"])
def api_indicators(symbol):
    """RSI + MACD จาก Alpha Vantage"""
    symbol = symbol.upper()
    cache_key = f"indicators_{symbol}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    if not ALPHA_VANTAGE_API_KEY:
        return jsonify({"error": "ALPHA_VANTAGE_API_KEY not set"}), 500

    try:
        # RSI
        rsi_url = (
            f"{ALPHA_VANTAGE_BASE}?function=RSI"
            f"&symbol={symbol}&interval=daily&time_period=14"
            f"&series_type=close&apikey={ALPHA_VANTAGE_API_KEY}"
        )
        rsi_res = requests.get(rsi_url, timeout=5).json()
        rsi_value = None
        if "Technical Analysis: RSI" in rsi_res:
            latest = sorted(rsi_res["Technical Analysis: RSI"].keys())[-1]
            rsi_value = float(rsi_res["Technical Analysis: RSI"][latest]["RSI"])

        # MACD
        macd_url = (
            f"{ALPHA_VANTAGE_BASE}?function=MACD"
            f"&symbol={symbol}&interval=daily&series_type=close"
            f"&apikey={ALPHA_VANTAGE_API_KEY}"
        )
        macd_res = requests.get(macd_url, timeout=5).json()
        macd_val = None
        macd_sig = None
        if "Technical Analysis: MACD" in macd_res:
            latest = sorted(macd_res["Technical Analysis: MACD"].keys())[-1]
            macd_val = float(macd_res["Technical Analysis: MACD"][latest]["MACD"])
            macd_sig = float(macd_res["Technical Analysis: MACD"][latest]["MACD_Signal"])

        rsi_label = None
        if rsi_value:
            if rsi_value > 70:
                rsi_label = "Overbought"
            elif rsi_value < 30:
                rsi_label = "Oversold"
            else:
                rsi_label = "Neutral"

        result = {
            "symbol": symbol,
            "rsi": round(rsi_value, 2) if rsi_value else None,
            "macd": round(macd_val, 4) if macd_val else None,
            "macd_signal": round(macd_sig, 4) if macd_sig else None,
            "rsi_interpretation": rsi_label,
        }
        cache_set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Indicators API error: {e}")
        return jsonify({"error": "Failed to fetch indicators"}), 500


@app.route("/api/health-score/<symbol>", methods=["GET"])
def api_health_score(symbol):
    """คำนวณคะแนนสุขภาพหุ้น (0–100) จาก financials"""
    symbol = symbol.upper()
    try:
        financials_resp = api_financials(symbol)
        if financials_resp.status_code != 200:
            return jsonify({"symbol": symbol, "health_score": None, "reasons": []})

        fin = financials_resp.get_json()
        score = 50
        reasons = []

        pe = fin.get("pe_ratio", 0) or 0
        if 10 < pe < 30:
            score += 10
            reasons.append("P/E อยู่ในโซนเหมาะสม")
        elif pe > 50:
            score -= 10
            reasons.append("P/E ค่อนข้างสูง")

        margin = fin.get("profit_margin", 0) or 0
        if margin > 15:
            score += 15
            reasons.append("กำไรสุทธิแข็งแรง")
        elif margin < 0:
            score -= 20
            reasons.append("กำไรสุทธิเป็นลบ")

        dte = fin.get("debt_to_equity", 0) or 0
        if 0 < dte < 2:
            score += 10
            reasons.append("โครงสร้างหนี้สมดุล")
        elif dte > 5:
            score -= 15
            reasons.append("หนี้สินสูง")

        fcf = fin.get("free_cash_flow", 0) or 0
        if fcf > 0:
            score += 10
            reasons.append("กระแสเงินสดอิสระเป็นบวก")

        eps_g = fin.get("eps_growth_5y", 0) or 0
        if eps_g > 0:
            score += 10
            reasons.append("EPS เติบโตในระยะยาว")

        score = max(0, min(100, score))
        interp = "Strong" if score >= 70 else "Moderate" if score >= 50 else "Weak"

        return jsonify({
            "symbol": symbol,
            "health_score": score,
            "reasons": reasons,
            "interpretation": interp
        })
    except Exception as e:
        logger.error(f"Health score error: {e}")
        return jsonify({"symbol": symbol, "health_score": None, "reasons": []})


@app.route("/health")
def health():
    return jsonify({"status": "OK", "timestamp": datetime.now().isoformat()})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
