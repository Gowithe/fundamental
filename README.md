# 📊 Stock Analyzer - Professional Trading Dashboard

A full-stack web application for comprehensive stock analysis using Flask backend and modern HTML/CSS/JS frontend.

## 🌟 Features

✅ **Real-time Stock Data** - Current prices, market data via Finnhub API  
✅ **Company Overview** - Industry, market cap, CEO info  
✅ **Financial Metrics** - Revenue, EPS, margins, debt ratios  
✅ **Valuation Ratios** - P/E, P/S, P/B, PEG ratios  
✅ **Technical Indicators** - RSI, MACD from Alpha Vantage  
✅ **Latest News** - Top company news articles  
✅ **Risk Analysis** - Automated risk factor assessment  
✅ **Price Chart** - 30-day price history visualization  
✅ **Dark Mode UI** - Modern, professional dark theme  
✅ **Responsive Design** - Works on desktop and mobile  
✅ **Production Ready** - Error handling, CORS support, Render deployment  

---

## 📁 Project Structure

```
stock_analyzer/
├── app.py                    # Flask backend (main server)
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment config
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── templates/
│   └── index.html          # HTML frontend
└── static/
    ├── css/
    │   └── styles.css      # Dark mode styling
    └── js/
        └── main.js         # Frontend logic
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- Git

### Step 1: Clone/Download the Project
```bash
# If you have git
git clone <repository-url>
cd stock_analyzer

# Or download the files manually and extract
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Step 5: Test the Application
1. Open browser: http://localhost:5000
2. Search for a stock symbol (e.g., AAPL, TSLA, MSFT)
3. View real-time data, charts, and analysis

---

## 🔑 API Configuration

The app comes with API keys already configured:

```python
FINNHUB_API_KEY = "d46ntu1r01qgc9etnfngd46ntu1r01qgc9etnfo0"
ALPHA_VANTAGE_API_KEY = "SSHS1YDZEUU1VQM0"
```

**API Details:**
- **Finnhub**: Provides stock prices, fundamentals, news
- **Alpha Vantage**: Provides technical indicators (RSI, MACD)

### To Replace API Keys

Edit `app.py` line 10-11:

```python
FINNHUB_API_KEY = "your_new_key_here"
ALPHA_VANTAGE_API_KEY = "your_new_key_here"
```

### How to Get Free API Keys

1. **Finnhub API** (Recommended)
   - Visit: https://finnhub.io/
   - Sign up for free account
   - Get API key from dashboard

2. **Alpha Vantage API**
   - Visit: https://www.alphavantage.co/
   - Sign up and get free API key

---

## 📊 API Endpoints

### Backend Endpoints (for reference)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/price/<symbol>` | GET | Current stock price & market data |
| `/api/news/<symbol>` | GET | Latest company news (8 articles) |
| `/api/financials/<symbol>` | GET | Financial metrics (EPS, margins, etc.) |
| `/api/overview/<symbol>` | GET | Company info & overview |
| `/api/indicators/<symbol>` | GET | Technical indicators (RSI, MACD) |
| `/api/dummy` | GET | Dummy data for testing |

**Example Request:**
```bash
curl http://localhost:5000/api/price/AAPL
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "current_price": 235.75,
  "change": 2.50,
  "change_percent": 1.07,
  "open": 233.25,
  "high": 236.50,
  "low": 232.75,
  "status": "success"
}
```

---

## 🌐 Deployment to Render

### Step 1: Prepare Files
Ensure you have:
- `app.py`
- `requirements.txt`
- `Procfile`
- `templates/index.html`
- `static/css/styles.css`
- `static/js/main.js`

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Stock Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-analyzer.git
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Set configuration:
   - **Name:** `stock-analyzer`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
5. Click "Create Web Service"
6. Wait for deployment (2-3 minutes)
7. Your app will be at: `https://stock-analyzer-XXXX.onrender.com`

### Step 4: Set Environment Variables (Optional)
In Render dashboard → Environment:
```
FINNHUB_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

---

## 🎨 Features Explained

### 1. Price Card
- Shows current price with change percentage
- Color-coded (green for up, red for down)
- Displays open, high, low prices

### 2. Company Overview
- Company name, industry, employees
- Website link, IPO date
- Company description

### 3. Financial Health Cards
- Revenue YoY growth
- Profit margin percentage
- EPS (Earnings Per Share)
- Debt to Equity ratio
- Free Cash Flow
- Return on Equity

### 4. Valuation Ratios
- P/E Ratio (Price-to-Earnings)
- Forward P/E
- PEG Ratio (Price/Earnings Growth)
- P/S Ratio (Price-to-Sales)
- P/B Ratio (Price-to-Book)

### 5. Technical Indicators
- RSI (Relative Strength Index) - 0-100 scale
- MACD (Moving Average Convergence Divergence)

### 6. Latest News
- Top 8 company news articles
- Clickable links to full articles
- Publication date and source

### 7. Risk Analysis
- Automated risk assessment
- Based on financial metrics
- Color-coded risk levels

### 8. AI Insight
- Investment recommendations
- Fundamental analysis summary
- Disclaimer on financial advice

---

## 🛠️ Customization

### Change Theme Colors

Edit `static/css/styles.css` - Root variables (line 2):

```css
:root {
    --accent-green: #10b981;      /* Change green color */
    --accent-red: #ef4444;        /* Change red color */
    --accent-blue: #3b82f6;       /* Change blue color */
}
```

### Add More Stock Symbols

Just search in the search box! Any symbol traded on major exchanges will work.

### Modify UI Text

Edit `templates/index.html` to change:
- Header text
- Section titles
- Placeholder text
- Disclaimers

---

## 🐛 Troubleshooting

### Issue: "Symbol not found" error
**Solution:** Make sure the stock symbol is correct (e.g., AAPL, not Apple)

### Issue: API returns no data
**Solution:** 
- Check internet connection
- Verify API keys are correct
- Wait a minute and try again (API rate limiting)
- Finnhub free tier: 60 requests/minute
- Alpha Vantage free tier: 5 requests/minute

### Issue: Port 5000 already in use
**Solution:**
```bash
# Use different port
python app.py --port 5001
# Or kill process on port 5000
```

### Issue: CSS not loading on Render
**Solution:** Ensure `static/css/styles.css` file exists and path is correct

### Issue: Charts not displaying
**Solution:** Make sure Chart.js CDN is loading (check browser console for errors)

---

## 📈 Performance Tips

1. **Cache API responses** - Add caching layer for frequently requested symbols
2. **Rate limiting** - Implement to avoid API throttling
3. **Pagination** - Load news articles on demand
4. **Image optimization** - Compress company logos
5. **Minify CSS/JS** - For production deployment

---

## 🔐 Security Notes

⚠️ **Important:**
- API keys are stored in backend (`app.py`) - NEVER expose to frontend
- Frontend communicates with backend only, not external APIs
- On Render, use Environment Variables for API keys:
  ```bash
  export FINNHUB_API_KEY="your_key"
  export ALPHA_VANTAGE_API_KEY="your_key"
  ```

---

## 📝 Testing

### Test with Dummy Data
```bash
curl http://localhost:5000/api/dummy
```

### Test Real API
```bash
# Test with AAPL
curl http://localhost:5000/api/price/AAPL
curl http://localhost:5000/api/overview/AAPL
curl http://localhost:5000/api/financials/AAPL
```

---

## 📚 Resources

- **Finnhub API Docs:** https://finnhub.io/docs/api
- **Alpha Vantage Docs:** https://www.alphavantage.co/documentation/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Chart.js Documentation:** https://www.chartjs.org/docs/latest/

---

## 📄 License

This project is open source and available for personal and commercial use.

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check browser console for errors (F12)
4. Verify network requests in browser dev tools

---

## ✨ Future Enhancements

- [ ] User authentication & watchlists
- [ ] Portfolio tracking
- [ ] Advanced charting (TradingView widgets)
- [ ] Cryptocurrency support
- [ ] Email alerts
- [ ] Historical data export
- [ ] Multi-language support (Thai, Chinese, etc.)
- [ ] Mobile app version
- [ ] Machine learning predictions

---

**Last Updated:** 2025  
**Status:** ✅ Production Ready

Enjoy analyzing stocks! 📊📈
