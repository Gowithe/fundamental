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

function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined || isNaN(num)) return "--";
  return Number(num).toFixed(decimals);
}

function formatPercent(num) {
  if (num === null || num === undefined || isNaN(num)) return "--";
  return Number(num * 100).toFixed(2) + "%";
}

function formatPercentDirect(num) {
  if (num === null || num === undefined || isNaN(num)) return "--";
  return Number(num).toFixed(2) + "%";
}

function formatMarketCap(m) {
  if (!m || isNaN(m)) return "--";
  if (m >= 1000) return (m / 1000).toFixed(2) + " B";
  return m.toFixed(2) + " M";
}

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  return res.json();
}

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
    console.error(err);
    showError("ดึงข้อมูลไม่สำเร็จ กรุณาลองใหม่ หรือตรวจสอบสัญลักษณ์หุ้น");
  } finally {
    showLoading(false);
  }
}

function renderPrice(price, overview) {
  document.getElementById("companyName").textContent =
    overview.name || price.symbol;
  document.getElementById("companySymbol").textContent = price.symbol;

  const logo = document.getElementById("companyLogo");
  if (overview.logo) {
    logo.src = overview.logo;
  } else {
    logo.src = "https://via.placeholder.com/40x40.png?text=?"; // placeholder
  }

  const current = document.getElementById("currentPrice");
  current.textContent = "$" + formatNumber(price.current_price, 2);

  const change = document.getElementById("priceChange");
  const changePercent = document.getElementById("priceChangePercent");
  change.textContent = (price.change >= 0 ? "+" : "") + formatNumber(price.change, 2);
  changePercent.textContent =
    "(" +
    (price.change_percent >= 0 ? "+" : "") +
    formatNumber(price.change_percent, 2) +
    "%)";

  const badge = document.getElementById("priceBadge");
  if (price.change > 0) {
    badge.style.background = "rgba(22, 163, 74, 0.15)";
    badge.style.color = "#bbf7d0";
  } else if (price.change < 0) {
    badge.style.background = "rgba(239, 68, 68, 0.15)";
    badge.style.color = "#fecaca";
  } else {
    badge.style.background = "rgba(148, 163, 184, 0.2)";
    badge.style.color = "#e5e7eb";
  }

  document.getElementById("openPrice").textContent =
    "$" + formatNumber(price.open, 2);
  document.getElementById("highPrice").textContent =
    "$" + formatNumber(price.high, 2);
  document.getElementById("lowPrice").textContent =
    "$" + formatNumber(price.low, 2);
}

function renderOverview(overview, healthScore) {
  document.getElementById("industry").textContent = overview.industry || "N/A";
  document.getElementById("marketCap").textContent = formatMarketCap(
    overview.market_cap
  );
  document.getElementById("country").textContent = overview.country || "N/A";
  document.getElementById("website").textContent = overview.website || "N/A";
  document.getElementById("employees").textContent =
    overview.employees || "N/A";
  document.getElementById("ipoDate").textContent = overview.ipo_date || "N/A";
  document.getElementById("description").textContent =
    overview.description || "ไม่มีข้อมูล";

  const score = healthScore.health_score ?? null;
  const scoreNum = document.getElementById("healthScore");
  const gauge = document.getElementById("scoreGauge");
  const interpretation = document.getElementById("scoreInterpretation");
  const reasonsUl = document.getElementById("scoreReasons");

  if (score === null) {
    scoreNum.textContent = "--";
    gauge.style.transform = "rotate(0deg)";
    interpretation.textContent = "ยังไม่สามารถคำนวณคะแนนได้";
    reasonsUl.innerHTML = "";
    return;
  }

  scoreNum.textContent = score;
  const angle = (score / 100) * 180 - 90; // -90 ถึง +90
  gauge.style.transform = `rotate(${angle}deg)`;

  let labelThai = "อ่อนแอ";
  if (score >= 70) labelThai = "แข็งแรง";
  else if (score >= 50) labelThai = "ปานกลาง";

  interpretation.textContent = `ภาพรวมสุขภาพหุ้น: ${labelThai} (${healthScore.interpretation})`;
  reasonsUl.innerHTML = "";
  (healthScore.reasons || []).forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r;
    reasonsUl.appendChild(li);
  });
}

function renderFinancials(f) {
  document.getElementById("peRatio").textContent = formatNumber(f.pe_ratio);
  document.getElementById("forwardPE").textContent = formatNumber(f.forward_pe);
  document.getElementById("pegRatio").textContent = formatNumber(f.peg_ratio);
  document.getElementById("profitMargin").textContent =
    formatNumber(f.profit_margin) + "%";
  document.getElementById("eps").textContent = formatNumber(
    f.earnings_per_share
  );
  document.getElementById("revenueGrowth").textContent =
    formatNumber(f.revenue_growth_5y * 100) + "%";
  document.getElementById("debtEquity").textContent = formatNumber(
    f.debt_to_equity
  );
  document.getElementById("freeCashFlow").textContent = formatNumber(
    f.free_cash_flow
  );

  document.getElementById("operatingMargin").textContent =
    formatNumber(f.operating_margin) + "%";
  document.getElementById("grossMargin").textContent =
    formatNumber(f.gross_margin) + "%";
  document.getElementById("roe").textContent =
    formatNumber(f.return_on_equity) + "%";
  document.getElementById("roa").textContent =
    formatNumber(f.return_on_assets) + "%";
  document.getElementById("epsGrowth").textContent =
    formatNumber(f.eps_growth_5y * 100) + "%";
  document.getElementById("quickRatio").textContent = formatNumber(
    f.quick_ratio
  );
  document.getElementById("fcfPerShare").textContent = formatNumber(
    f.free_cash_flow_per_share
  );
  document.getElementById("debtToAssets").textContent = formatNumber(
    f.debt_to_assets
  );
}

function renderNews(newsData) {
  const list = document.getElementById("newsList");
  list.innerHTML = "";

  const items = newsData.news || [];
  if (!items.length) {
    list.innerHTML = "<p>ยังไม่มีข่าวล่าสุด</p>";
    return;
  }

  items.forEach((n) => {
    const div = document.createElement("div");
    div.className = "news-item";
    const dt = n.datetime
      ? new Date(n.datetime * 1000).toLocaleString("th-TH")
      : "";

    div.innerHTML = `
      <h4>${n.headline}</h4>
      <p>${n.summary || ""}</p>
      <p class="news-meta">${n.source || ""} · ${dt}</p>
      ${
        n.url
          ? `<a href="${n.url}" target="_blank" rel="noopener">อ่านข่าว</a>`
          : ""
      }
    `;
    list.appendChild(div);
  });
}

function renderIndicators(ind, f, health) {
  const rsiVal = document.getElementById("rsiValue");
  const rsiStatus = document.getElementById("rsiStatus");
  const macdVal = document.getElementById("macdValue");
  const macdStatus = document.getElementById("macdStatus");
  const macdSignal = document.getElementById("macdSignal");
  const signalStatus = document.getElementById("signalStatus");
  const riskBox = document.getElementById("riskFactors");
  const aiBox = document.getElementById("aiInsight");

  if (ind.error) {
    rsiVal.textContent = "--";
    rsiStatus.textContent = "โหลด RSI ไม่สำเร็จ";
    macdVal.textContent = "--";
    macdSignal.textContent = "--";
    macdStatus.textContent = "โหลด MACD ไม่สำเร็จ";
    signalStatus.textContent = "";
  } else {
    rsiVal.textContent = ind.rsi ? formatNumber(ind.rsi, 2) : "--";
    rsiStatus.textContent = ind.rsi_interpretation || "Neutral";

    macdVal.textContent = ind.macd ? formatNumber(ind.macd, 4) : "--";
    macdSignal.textContent = ind.macd_signal
      ? formatNumber(ind.macd_signal, 4)
      : "--";

    if (ind.macd && ind.macd_signal) {
      const diff = ind.macd - ind.macd_signal;
      if (diff > 0) {
        macdStatus.textContent = "MACD > Signal (โมเมนตัมบวก)";
        signalStatus.textContent = "สัญญาณระยะสั้นเป็นบวก";
      } else {
        macdStatus.textContent = "MACD < Signal (โมเมนตัมลบ)";
        signalStatus.textContent = "สัญญาณระยะสั้นเป็นลบ";
      }
    } else {
      macdStatus.textContent = "ข้อมูลไม่ครบ";
      signalStatus.textContent = "";
    }
  }

  const risks = [];
  if (f.debt_to_equity && f.debt_to_equity > 3) {
    risks.push("หนี้สินต่อทุนค่อนข้างสูง ควรระวังภาวะดอกเบี้ยขาขึ้น");
  }
  if (f.profit_margin && f.profit_margin < 5) {
    risks.push("กำไรสุทธิต่ำ อาจถูกกระทบจากต้นทุนและการแข่งขัน");
  }
  if (health.health_score && health.health_score < 50) {
    risks.push("คะแนนสุขภาพโดยรวมอยู่ในระดับค่อนข้างอ่อนแอ");
  }

  if (!risks.length) {
    risks.push("ยังไม่พบสัญญาณความเสี่ยงหลักจากตัวเลขเบื้องต้น");
  }

  riskBox.innerHTML = risks
    .map((r) => `<p>• ${r}</p>`)
    .join("");

  // set default AI insight text
  aiBox.innerHTML =
    "<p>กดปุ่มด้านล่างเพื่อสร้างมุมมองเชิงวิเคราะห์จากตัวเลขเบื้องต้น</p>";
}

function generateNewInsight() {
  const box = document.getElementById("aiInsight");
  const templates = [
    "จากตัวเลขกำไรสุทธิและระดับหนี้สิน หุ้นตัวนี้มีโครงสร้างทางการเงินที่ค่อนข้างแข็งแรง เหมาะกับนักลงทุนที่รับความเสี่ยงปานกลางได้ และต้องการเติบโตในระยะยาว",
    "อัตรากำไรสุทธิอยู่ในระดับที่น่าสนใจ แต่หนี้สินต่อทุนยังต้องจับตา แนะนำให้ดูแนวโน้มงบไตรมาสถัดไปประกอบก่อนตัดสินใจลงทุนเพิ่ม",
    "กระแสเงินสดอิสระเป็นบวกและเติบโตดี แสดงถึงความสามารถในการสร้างเงินสดของธุรกิจ เหมาะกับแนวคิดการถือยาวและเก็บ DCA ต่อเนื่อง",
    "ตัวเลขหลายด้านสะท้อนว่าบริษัทกำลังอยู่ในช่วงเปลี่ยนผ่าน แนะนำให้โฟกัสที่แผนธุรกิจในอนาคต และความสามารถในการรักษาอัตรากำไร",
  ];
  const idx = Math.floor(Math.random() * templates.length);
  box.innerHTML = `<p>${templates[idx]}</p>`;
}

/* Tabs */
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll(".tab-btn")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    const tabId = btn.dataset.tab + "-tab";
    document
      .querySelectorAll(".tab-content")
      .forEach((t) => t.classList.remove("active"));
    document.getElementById(tabId).classList.add("active");
  });
});

/* Events */
searchBtn.addEventListener("click", () => {
  analyzeSymbol(searchInput.value);
});

searchInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    analyzeSymbol(searchInput.value);
  }
});
