// ============ CONFIG: เปลี่ยนตรงนี้อย่างเดียว ===============
const API_BASE =
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000"
    : "https://fundamental-micb.onrender.com";
// ===============================================================

const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const welcomeSection = document.getElementById("welcomeSection");
const dataSection = document.getElementById("dataSection");
const loadingSpinner = document.getElementById("loadingSpinner");
const errorAlert = document.getElementById("errorAlert");
const errorMessage = document.getElementById("errorMessage");

function showLoading(show) {
  loadingSpinner.classList.toggle("hidden", !show);
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorAlert.classList.remove("hidden");
}

function clearError() {
  errorAlert.classList.add("hidden");
  errorMessage.textContent = "";
}

async function fetchJSON(url) {
  const fullURL = `${API_BASE}${url}`;
  console.log("📡 Fetch:", fullURL);

  const res = await fetch(fullURL);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  return res.json();
}

// ---------------------- Core Function ----------------------
async function analyzeSymbol(symbol) {
  symbol = symbol.trim().toUpperCase();
  if (!symbol) {
    showError("กรุณาใส่สัญลักษณ์หุ้น");
    return;
  }

  clearError();
  showLoading(true);

  try {
    const [price, overview, financials, news, indicators, healthScore] =
      await Promise.all([
        fetchJSON(`/api/price/${symbol}`),
        fetchJSON(`/api/overview/${symbol}`),
        fetchJSON(`/api/financials/${symbol}`),
        fetchJSON(`/api/news/${symbol}`),
        fetchJSON(`/api/indicators/${symbol}`),
        fetchJSON(`/api/health-score/${symbol}`),
      ]);

    renderPrice(price, overview);
    renderOverview(overview, healthScore);
    renderFinancials(financials);
    renderNews(news);
    renderIndicators(indicators, financials, healthScore);

    welcomeSection.classList.add("hidden");
    dataSection.classList.remove("hidden");
  } catch (err) {
    console.error("❌ Error:", err);
    showError("ดึงข้อมูลไม่สำเร็จ กรุณาลองใหม่ หรือตรวจสอบสัญลักษณ์หุ้น");
  } finally {
    showLoading(false);
  }
}
