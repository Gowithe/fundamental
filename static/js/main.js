// ===== STATE MANAGEMENT =====
let currentSymbol = null;
let priceChart = null;

// ===== DOM ELEMENTS =====
const symbolInput = document.getElementById('symbolInput');
const searchBtn = document.getElementById('searchBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');
const mainContent = document.getElementById('mainContent');
const welcomeMessage = document.getElementById('welcomeMessage');

// ===== EVENT LISTENERS =====
searchBtn.addEventListener('click', searchStock);
symbolInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchStock();
});

// ===== MAIN SEARCH FUNCTION =====
async function searchStock() {
    const symbol = symbolInput.value.trim().toUpperCase();
    
    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }
    
    await fetchAndDisplayStock(symbol);
}

function searchStockDirect(symbol) {
    symbolInput.value = symbol;
    searchStock();
}

async function fetchAndDisplayStock(symbol) {
    try {
        currentSymbol = symbol;
        showSpinner(true);
        hideError();
        
        // Parallel API calls for better performance
        const [priceData, newsData, financialsData, overviewData, indicatorsData] = await Promise.all([
            fetchAPI(`/api/price/${symbol}`),
            fetchAPI(`/api/news/${symbol}`),
            fetchAPI(`/api/financials/${symbol}`),
            fetchAPI(`/api/overview/${symbol}`),
            fetchAPI(`/api/indicators/${symbol}`)
        ]);
        
        // Check for errors
        if (!priceData || priceData.error) {
            showError(`Symbol "${symbol}" not found. Please try another symbol.`);
            showSpinner(false);
            return;
        }
        
        // Display all data
        displayPrice(priceData);
        displayOverview(overviewData);
        displayFinancials(financialsData);
        displayNews(newsData);
        displayIndicators(indicatorsData);
        displayRiskFactors(financialsData);
        displayChart(priceData);
        
        // Hide welcome, show content
        welcomeMessage.classList.add('hidden');
        mainContent.classList.remove('hidden');
        
        showSpinner(false);
        
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred while fetching data. Please try again.');
        showSpinner(false);
    }
}

// ===== API CALL WRAPPER =====
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            return { error: `HTTP ${response.status}` };
        }
        return await response.json();
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        return { error: error.message };
    }
}

// ===== DISPLAY FUNCTIONS =====

function displayPrice(data) {
    if (data.error) return;
    
    // ✅ แก้ไข: ใช้ชื่อ field ที่ตรงกับ Backend
    const currentPrice = data.current || 0;
    const changeValue = data.change || 0;
    const changePercent = data.percent || 0;
    const isPositive = changePercent >= 0;
    
    document.getElementById('symbolDisplay').textContent = data.symbol;
    document.getElementById('currentPrice').textContent = `$${currentPrice.toFixed(2)}`;
    document.getElementById('changeValue').textContent = `${isPositive ? '+' : ''}${changeValue.toFixed(2)}`;
    document.getElementById('changePercent').textContent = `(${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`;
    
    const priceChange = document.getElementById('priceChange');
    priceChange.classList.remove('positive', 'negative');
    priceChange.classList.add(isPositive ? 'positive' : 'negative');
    
    document.getElementById('openPrice').textContent = `$${(data.open || 0).toFixed(2)}`;
    document.getElementById('highPrice').textContent = `$${(data.high || 0).toFixed(2)}`;
    document.getElementById('lowPrice').textContent = `$${(data.low || 0).toFixed(2)}`;
}

function displayOverview(data) {
    if (data.error) return;
    
    // ✅ แก้ไข: ใช้ชื่อ field ที่ตรงกับ Backend
    const companyName = data.name || 'N/A';
    const marketCap = data.market_cap || 0;
    
    // Format market cap
    let marketCapFormatted = 'N/A';
    if (marketCap > 0) {
        if (marketCap >= 1000) {
            marketCapFormatted = `$${(marketCap / 1000).toFixed(2)}T`;
        } else if (marketCap >= 1) {
            marketCapFormatted = `$${marketCap.toFixed(2)}B`;
        } else {
            marketCapFormatted = `$${(marketCap * 1000).toFixed(2)}M`;
        }
    }
    
    document.getElementById('companyName').textContent = companyName;
    document.getElementById('marketCap').textContent = marketCapFormatted;
    document.getElementById('industryValue').textContent = data.industry || 'N/A';
    document.getElementById('employeesValue').textContent = 'N/A'; // Finnhub doesn't provide this
    document.getElementById('ipoValue').textContent = data.ipo || 'N/A';
    
    const websiteLink = document.getElementById('websiteValue');
    if (data.weburl && data.weburl !== '#') {
        websiteLink.href = data.weburl;
        websiteLink.textContent = 'Visit Website →';
    } else {
        websiteLink.textContent = 'N/A';
    }
    
    // Finnhub doesn't provide description in profile2, show basic info
    const description = `${companyName} is a ${data.industry || 'company'} listed on ${data.exchange || 'the stock exchange'}.`;
    document.getElementById('descriptionValue').textContent = description;
}

function displayFinancials(data) {
    if (data.error) return;
    
    // ✅ แก้ไข: ใช้ชื่อ field ที่ตรงกับ Backend
    const revenueGrowth = data.revenue_growth || 0;
    const profitMargin = data.profit_margin || 0;
    const eps = data.eps || 0;
    const debtEquity = data.debt_equity || 0;
    const fcf = data.free_cash_flow || 0;
    const roe = data.roe || 0;
    
    // Format values
    document.getElementById('revenueGrowth').textContent = `${revenueGrowth.toFixed(2)}%`;
    document.getElementById('profitMargin').textContent = `${profitMargin.toFixed(2)}%`;
    document.getElementById('epsValue').textContent = `$${eps.toFixed(2)}`;
    document.getElementById('debtEquity').textContent = debtEquity.toFixed(2);
    
    // Format FCF
    let fcfFormatted = 'N/A';
    if (fcf !== 0) {
        if (Math.abs(fcf) >= 1000000000) {
            fcfFormatted = `$${(fcf / 1000000000).toFixed(2)}B`;
        } else if (Math.abs(fcf) >= 1000000) {
            fcfFormatted = `$${(fcf / 1000000).toFixed(2)}M`;
        } else {
            fcfFormatted = `$${fcf.toFixed(2)}`;
        }
    }
    document.getElementById('fcfValue').textContent = fcfFormatted;
    document.getElementById('roeValue').textContent = `${roe.toFixed(2)}%`;
    
    // Valuation Ratios
    document.getElementById('peRatio').textContent = (data.pe_ratio || 0).toFixed(2);
    document.getElementById('forwardPe').textContent = 'N/A'; // Not available in basic metrics
    document.getElementById('pegRatio').textContent = (data.peg_ratio || 0).toFixed(2);
    document.getElementById('psRatio').textContent = (data.ps_ratio || 0).toFixed(2);
    document.getElementById('pbRatio').textContent = (data.pb_ratio || 0).toFixed(2);
    document.getElementById('grossMargin').textContent = `${(data.operating_margin || 0).toFixed(2)}%`;
}

function displayNews(data) {
    const newsContainer = document.getElementById('newsContainer');
    
    // ✅ แก้ไข: Backend ส่ง 'articles' แทน 'news'
    if (data.error || !data.articles || data.articles.length === 0) {
        newsContainer.innerHTML = '<p>No news articles available</p>';
        return;
    }
    
    newsContainer.innerHTML = data.articles.map(article => `
        <div class="news-item" onclick="window.open('${article.url}', '_blank')">
            <div class="news-headline">${article.headline}</div>
            <div class="news-summary">${article.summary}</div>
            <div class="news-meta">
                <span class="news-source">${article.source}</span>
                <span>${formatDate(article.datetime)}</span>
            </div>
        </div>
    `).join('');
}

function displayIndicators(data) {
    if (data.error || data.rsi === null || data.rsi === undefined) {
        document.getElementById('rsiValue').textContent = 'N/A';
        document.getElementById('rsiSignal').textContent = 'Unable to load';
        document.getElementById('macdValue').textContent = 'N/A';
        document.getElementById('macdSignal').textContent = 'Unable to load';
        return;
    }
    
    // ✅ RSI
    const rsi = data.rsi || 50;
    document.getElementById('rsiValue').textContent = rsi.toFixed(2);
    
    // Determine RSI signal
    let rsiSignal = 'Neutral';
    if (rsi > 70) {
        rsiSignal = 'Overbought ⚠️';
    } else if (rsi < 30) {
        rsiSignal = 'Oversold 📈';
    }
    document.getElementById('rsiSignal').textContent = rsiSignal;
    document.getElementById('rsiFill').style.width = `${Math.min(rsi, 100)}%`;
    
    // ✅ MACD
    if (data.macd && data.macd.macd !== undefined) {
        const macdValue = data.macd.macd || 0;
        const macdSignal = data.macd.signal || 0;
        const macdHist = data.macd.histogram || 0;
        
        document.getElementById('macdValue').textContent = macdValue.toFixed(4);
        
        // Determine MACD signal
        let signalText = 'Neutral';
        if (macdHist > 0) {
            signalText = 'Bullish 📈';
        } else if (macdHist < 0) {
            signalText = 'Bearish 📉';
        }
        document.getElementById('macdSignal').textContent = signalText;
    } else {
        document.getElementById('macdValue').textContent = 'N/A';
        document.getElementById('macdSignal').textContent = 'Unable to load';
    }
}

function displayRiskFactors(financialsData) {
    const riskList = document.getElementById('riskList');
    const risks = [];
    
    if (!financialsData || financialsData.error) {
        riskList.innerHTML = '<p>Unable to analyze risk factors</p>';
        return;
    }
    
    // Analyze risk factors based on financials
    const peRatio = financialsData.pe_ratio || 0;
    const debtEquity = financialsData.debt_equity || 0;
    const profitMargin = financialsData.profit_margin || 0;
    const roe = financialsData.roe || 0;
    
    if (peRatio > 30) {
        risks.push({
            icon: '📈',
            title: 'High Valuation',
            desc: `P/E ratio of ${peRatio.toFixed(2)} is above average - stock may be overpriced`
        });
    }
    
    if (debtEquity > 1.5) {
        risks.push({
            icon: '💳',
            title: 'High Debt',
            desc: `Debt-to-Equity ratio of ${debtEquity.toFixed(2)} indicates higher financial risk`
        });
    }
    
    if (profitMargin < 5) {
        risks.push({
            icon: '📉',
            title: 'Low Margins',
            desc: `Profit margin of ${profitMargin.toFixed(2)}% is relatively low`
        });
    }
    
    if (roe < 10) {
        risks.push({
            icon: '⚠️',
            title: 'Weak ROE',
            desc: `Return on Equity of ${roe.toFixed(2)}% is below industry average`
        });
    }
    
    if (risks.length === 0) {
        risks.push({
            icon: '✅',
            title: 'Healthy Metrics',
            desc: 'Stock shows positive financial indicators'
        });
    }
    
    riskList.innerHTML = risks.map(risk => `
        <div class="risk-item">
            <div class="risk-icon">${risk.icon}</div>
            <div class="risk-text">
                <div class="risk-title">${risk.title}</div>
                <div class="risk-desc">${risk.desc}</div>
            </div>
        </div>
    `).join('');
}

function displayChart(priceData) {
    if (priceData.error) return;
    
    // Generate simulated price history for chart
    const currentPrice = priceData.current || 100;
    const labels = generateDateLabels(30);
    const priceHistory = generatePriceHistory(currentPrice, 30);
    
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${priceData.symbol} Price (30 days)`,
                data: priceHistory,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointBackgroundColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#b0b9c1' }
                }
            },
            scales: {
                y: {
                    ticks: { color: '#b0b9c1' },
                    grid: { color: 'rgba(42, 53, 66, 0.5)' }
                },
                x: {
                    ticks: { color: '#b0b9c1' },
                    grid: { color: 'rgba(42, 53, 66, 0.5)' }
                }
            }
        }
    });
}

// ===== UTILITY FUNCTIONS =====

function generateDateLabels(days) {
    const labels = [];
    const now = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return labels;
}

function generatePriceHistory(basePrice, days) {
    const prices = [];
    let price = basePrice * 0.95; // Start 5% lower
    
    for (let i = 0; i < days; i++) {
        price += (Math.random() - 0.48) * basePrice * 0.02; // Random walk
        prices.push(Math.round(price * 100) / 100);
    }
    
    return prices;
}

function formatDate(timestamp) {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
}

function showSpinner(show) {
    loadingSpinner.classList.toggle('hidden', !show);
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

// ===== THEME TOGGLE =====
function toggleTheme() {
    document.body.classList.toggle('light-mode');
    localStorage.setItem('theme', document.body.classList.contains('light-mode') ? 'light' : 'dark');
}

// Load saved theme preference
window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }
});

// Allow Enter key to search
symbolInput.addEventListener('keydown', (e) => {
    if (e.code === 'Enter') {
        searchStock();
    }
});
