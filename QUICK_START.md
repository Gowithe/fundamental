# ⚡ Stock Analyzer - Quick Start Guide

Get the Stock Analyzer running in less than 5 minutes!

---

## 🎯 1-Minute Setup (Windows)

```bash
# 1. Navigate to project folder
cd stock_analyzer

# 2. Run the script
run.bat

# 3. Open browser: http://localhost:5000
# Done! 🎉
```

---

## 🎯 1-Minute Setup (macOS/Linux)

```bash
# 1. Navigate to project folder
cd stock_analyzer

# 2. Make script executable
chmod +x run.sh

# 3. Run the script
./run.sh

# 4. Open browser: http://localhost:5000
# Done! 🎉
```

---

## 📝 Manual Setup (All Platforms)

### Prerequisites
- Python 3.7+ installed
- pip package manager
- Terminal/Command Prompt access

### Step-by-Step

#### 1. Create Virtual Environment
```bash
python -m venv venv
```

#### 2. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
python app.py
```

#### 5. Open in Browser
```
http://localhost:5000
```

---

## 🧪 Test It Immediately

### Search for Stocks
Try these symbols:
- **AAPL** - Apple Inc.
- **TSLA** - Tesla
- **MSFT** - Microsoft
- **GOOGL** - Google Alphabet
- **AMZN** - Amazon

### Expected Results
✅ Real-time stock prices  
✅ Company information  
✅ Financial metrics  
✅ News articles  
✅ Technical indicators  
✅ Charts and graphs  

---

## 📱 Try Example Stocks (No Search Needed)

On the home page, click any of these buttons:
- 📊 AAPL
- 🚗 TSLA
- 💻 MSFT
- 📱 GOOGL

---

## 🐳 Quick Docker Setup

```bash
# Install Docker from: https://docker.com

# Run with Docker Compose (easiest)
docker-compose up

# Or use Docker CLI
docker build -t stock-analyzer .
docker run -p 5000:5000 stock-analyzer

# Open browser: http://localhost:5000
```

---

## ☁️ Deploy to Cloud (3 Minutes)

### Option A: Render (Recommended)

1. Push to GitHub:
```bash
git init
git add .
git commit -m "Stock Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-analyzer.git
git push -u origin main
```

2. Go to https://render.com
3. Click "New Web Service"
4. Connect GitHub & select repo
5. Set:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
6. Click Deploy
7. Done! Your app is live in 5 minutes

---

## 🔧 Configuration

### API Keys Already Included ✅

The app comes with working API keys:
- ✅ Finnhub API Key
- ✅ Alpha Vantage API Key

**To use your own keys:**

Edit `app.py` line 10-11:
```python
FINNHUB_API_KEY = "your_new_key_here"
ALPHA_VANTAGE_API_KEY = "your_new_key_here"
```

Get free API keys from:
- https://finnhub.io (Finnhub)
- https://alphavantage.co (Alpha Vantage)

---

## ✨ What's Included

✅ **Backend (Flask)**
- 5 main API endpoints
- Error handling & CORS support
- Production-ready with Gunicorn

✅ **Frontend (HTML/CSS/JS)**
- Modern dark theme UI
- Real-time price updates
- Interactive charts (Chart.js)
- Responsive design (mobile-friendly)

✅ **Data Sources**
- Finnhub: Stock prices, fundamentals, news
- Alpha Vantage: Technical indicators

✅ **Features**
- Price tracking with % change
- Company overview
- 6 financial health metrics
- 6 valuation ratios
- Technical indicators (RSI, MACD)
- Latest news articles
- Risk analysis
- AI investment insights

✅ **Deployment Ready**
- Docker support
- Render/Heroku/AWS ready
- Environment variables support
- SSL/HTTPS compatible

---

## 🐛 Troubleshooting

### Port 5000 Already in Use
```bash
# Try different port
python app.py  # Change port in app.py last line
```

### Module Not Found Error
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### No Data Showing
```bash
# Check internet connection
# Wait 1 minute (API rate limiting)
# Try another stock symbol
```

### CSS/JS Not Loading
```bash
# Hard refresh browser
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (macOS)
```

---

## 🎨 Customize UI

### Change Colors
Edit `static/css/styles.css`:
```css
:root {
    --accent-green: #10b981;
    --accent-blue: #3b82f6;
    /* etc. */
}
```

### Change Text
Edit `templates/index.html`:
- Change section titles
- Update company name
- Modify descriptions

---

## 📊 API Endpoints (Reference)

```
GET  /                           → API status
GET  /api/price/<symbol>         → Current price
GET  /api/news/<symbol>          → Latest news
GET  /api/financials/<symbol>    → Financial metrics
GET  /api/overview/<symbol>      → Company info
GET  /api/indicators/<symbol>    → Technical indicators
GET  /api/dummy                  → Test data
```

---

## 📁 File Structure

```
stock_analyzer/
├── app.py                    # Flask backend
├── requirements.txt          # Python packages
├── Procfile                  # Render/Heroku config
├── Dockerfile               # Docker config
├── docker-compose.yml       # Docker Compose
├── run.sh / run.bat         # Quick run scripts
├── README.md                # Full documentation
├── DEPLOYMENT_GUIDE.md      # Deployment help
├── templates/
│   └── index.html          # Frontend
└── static/
    ├── css/styles.css      # Dark theme styling
    └── js/main.js          # Interactive logic
```

---

## ✅ Checklist: First Run

- [ ] Python 3.7+ installed
- [ ] Downloaded/cloned project
- [ ] Navigated to project folder
- [ ] Created virtual environment
- [ ] Activated virtual environment
- [ ] Installed dependencies
- [ ] Started Flask app
- [ ] Opened http://localhost:5000
- [ ] Searched for a stock
- [ ] Saw data and charts

If all ✅, you're ready to go! 🚀

---

## 🚀 Next Steps

1. **Customize** - Change colors, text, add features
2. **Deploy** - Push to Render, Heroku, AWS
3. **Share** - Send link to friends
4. **Enhance** - Add more features (watchlist, portfolio, etc.)

---

## 📚 More Help

- **Full README:** `README.md`
- **Deployment:** `DEPLOYMENT_GUIDE.md`
- **Issues?** Check troubleshooting section above
- **API Help:** https://finnhub.io/docs/api

---

## 🎉 You're All Set!

Enjoy your Stock Analyzer! 📊📈

**Questions? Need help?**
1. Check README.md
2. Check DEPLOYMENT_GUIDE.md
3. Check browser console (F12)
4. Check application logs

---

**Version:** 1.0  
**Last Updated:** 2025  
**Status:** ✅ Ready to Use
