/**
 * JobShield Platform Frontend Client Logic
 */

let sampleCases = [];
let allScams = [];

// Initialize application on DOM load
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  setupPresetDropdown();
  setupDragAndDrop();
  fetchSampleCases();
  loadScams();
  loadAcademicMetrics();
});

// Navigation Tab Switcher
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll(".nav-tab").forEach(el => el.classList.remove("active-tab"));

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) {
    targetTab.classList.remove("hidden");
  }

  const activeBtn = document.querySelector(`[data-tab="${tabId}"]`);
  if (activeBtn) {
    activeBtn.classList.add("active-tab");
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

// Preset Demo Dropdown
function setupPresetDropdown() {
  const btn = document.getElementById("quick-demo-btn");
  const menu = document.getElementById("demo-dropdown");
  if (!btn || !menu) return;

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.toggle("hidden");
  });

  document.addEventListener("click", () => {
    menu.classList.add("hidden");
  });
}

// Fetch Pre-configured Test Samples
async function fetchSampleCases() {
  try {
    const res = await fetch("/api/samples");
    if (res.ok) {
      sampleCases = await res.json();
    }
  } catch (err) {
    console.error("Failed to load sample cases:", err);
  }
}

// Load a specific sample case into the Job Scanner
function loadSampleCase(index) {
  if (!sampleCases || !sampleCases[index]) return;
  const sample = sampleCases[index];

  switchTab("scanner");

  document.getElementById("scan-title").value = sample.title || "";
  document.getElementById("scan-company").value = sample.company || "";
  document.getElementById("scan-salary").value = sample.salary || "";
  document.getElementById("scan-email").value = sample.contact_email || "";
  document.getElementById("scan-url").value = sample.portal_url || "";
  document.getElementById("scan-desc").value = sample.description || "";

  // Auto submit for rapid demonstration
  document.getElementById("scanner-form").dispatchEvent(new Event("submit"));
}

function clearScannerForm() {
  document.getElementById("scanner-form").reset();
  document.getElementById("results-placeholder").classList.remove("hidden");
  document.getElementById("results-card").classList.add("hidden");
  document.getElementById("explain-container").classList.add("hidden");
}

// Handle Job Scan Form Submission
async function handleJobScan(e) {
  e.preventDefault();
  const submitBtn = document.getElementById("scan-submit-btn");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span class="inline-block animate-spin mr-2">⚙️</span> Analyzing Indicators...`;

  const payload = {
    title: document.getElementById("scan-title").value.trim(),
    company: document.getElementById("scan-company").value.trim(),
    salary: document.getElementById("scan-salary").value.trim(),
    contact_email: document.getElementById("scan-email").value.trim(),
    portal_url: document.getElementById("scan-url").value.trim(),
    description: document.getElementById("scan-desc").value.trim()
  };

  try {
    const res = await fetch("/api/analyze/job", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error("Analysis failed");
    }

    const data = await res.json();
    renderAnalysisResults(data);

  } catch (err) {
    alert("Error executing analysis: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i data-lucide="shield-check" class="w-5 h-5"></i><span>Run Fraud Detection & Security Audit</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

// Render Results on Scanner Tab
function renderAnalysisResults(data) {
  document.getElementById("results-placeholder").classList.add("hidden");
  const card = document.getElementById("results-card");
  card.classList.remove("hidden");

  // Animate Score
  const scoreVal = document.getElementById("result-score-val");
  animateValue(scoreVal, 0, data.overall_fraud_score, 600);

  // Verdict & Badge
  const verdictEl = document.getElementById("result-verdict");
  const badgeEl = document.getElementById("result-threat-badge");
  const barEl = document.getElementById("result-score-bar");

  verdictEl.innerText = data.verdict;
  badgeEl.innerText = data.threat_level;

  let barColor = "bg-emerald-500";
  let badgeClasses = "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";

  if (data.overall_fraud_score >= 75) {
    barColor = "bg-rose-500";
    badgeClasses = "bg-rose-500/20 text-rose-300 border border-rose-500/30";
  } else if (data.overall_fraud_score >= 50) {
    barColor = "bg-orange-500";
    badgeClasses = "bg-orange-500/20 text-orange-300 border border-orange-500/30";
  } else if (data.overall_fraud_score >= 25) {
    barColor = "bg-amber-500";
    badgeClasses = "bg-amber-500/20 text-amber-300 border border-amber-500/30";
  }

  barEl.className = `h-full rounded-full transition-all duration-700 ${barColor}`;
  barEl.style.width = `${data.overall_fraud_score}%`;
  badgeEl.className = `mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${badgeClasses}`;

  // Summary
  document.getElementById("result-summary").innerText = data.summary;

  // Breakdown Bars
  const comp = data.component_scores || {};
  setBar("bar-fin", "bar-fin-val", comp.financial_risk || 0);
  setBar("bar-contact", "bar-contact-val", comp.contact_risk || 0);
  setBar("bar-comp", "bar-comp-val", comp.company_risk || 0);
  setBar("bar-ling", "bar-ling-val", comp.linguistic_risk || 0);
  setBar("bar-sal", "bar-sal-val", comp.salary_risk || 0);

  // Red Flags
  const flagsContainer = document.getElementById("red-flags-container");
  const countBadge = document.getElementById("red-flags-count");
  flagsContainer.innerHTML = "";
  countBadge.innerText = `${data.red_flags ? data.red_flags.length : 0} Flags`;

  if (!data.red_flags || data.red_flags.length === 0) {
    flagsContainer.innerHTML = `
      <div class="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-xl flex items-center gap-2">
        <i data-lucide="check-circle" class="w-4 h-4"></i>
        <span>No malicious recruitment indicators detected.</span>
      </div>
    `;
  } else {
    data.red_flags.forEach(flag => {
      const isCritical = flag.severity === "CRITICAL";
      const isHigh = flag.severity === "HIGH";
      const badgeColor = isCritical 
        ? "bg-rose-500/20 text-rose-300 border-rose-500/30" 
        : (isHigh ? "bg-orange-500/20 text-orange-300 border-orange-500/30" : "bg-amber-500/20 text-amber-300 border-amber-500/30");
      
      const item = document.createElement("div");
      item.className = "bg-dark-900/80 border border-slate-800 p-2.5 rounded-xl space-y-1";
      item.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-semibold text-slate-200 text-xs">${flag.rule}</span>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-full border ${badgeColor}">${flag.severity}</span>
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">${flag.detail}</p>
      `;
      flagsContainer.appendChild(item);
    });
  }

  // Explainable AI & Context Highlighter
  const explainBox = document.getElementById("explain-container");
  explainBox.classList.remove("hidden");
  document.getElementById("highlighted-text-box").innerHTML = data.annotated_text_html || "";

  // Recommendations
  const recsList = document.getElementById("recommendations-list");
  recsList.innerHTML = "";
  (data.safety_recommendations || []).forEach(rec => {
    const li = document.createElement("li");
    li.innerText = rec;
    recsList.appendChild(li);
  });

  if (window.lucide) lucide.createIcons();
}

function setBar(barId, valId, score) {
  const bar = document.getElementById(barId);
  const val = document.getElementById(valId);
  if (bar && val) {
    bar.style.width = `${score}%`;
    val.innerText = `${score}%`;
  }
}

function animateValue(el, start, end, duration) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    el.innerText = Math.floor(progress * (end - start) + start);
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

// ==========================================
// TAB 2: URL INSPECTOR
// ==========================================
function setTestUrl(url) {
  document.getElementById("inspect-url-input").value = url;
}

async function handleUrlScan(e) {
  e.preventDefault();
  const input = document.getElementById("inspect-url-input");
  const btn = document.getElementById("url-submit-btn");
  const resultBox = document.getElementById("url-result-box");

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin mr-1">⚙️</span> Inspecting...`;

  try {
    const res = await fetch("/api/analyze/url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: input.value.trim() })
    });

    if (!res.ok) throw new Error("URL Inspection failed");
    const data = await res.json();
    renderUrlResult(data);

  } catch (err) {
    alert("Error inspecting URL: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="search" class="w-4 h-4"></i><span>Inspect URL</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderUrlResult(data) {
  const box = document.getElementById("url-result-box");
  box.classList.remove("hidden");

  const ui = data.url_inspection || {};
  const isHighRisk = data.overall_fraud_score >= 50;

  box.innerHTML = `
    <div class="bg-dark-900 p-4 rounded-xl border border-slate-800 space-y-3">
      <div class="flex items-center justify-between">
        <div>
          <span class="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Target Domain</span>
          <div class="text-sm font-bold text-white font-mono">${ui.hostname || "unknown"}</div>
        </div>
        <div class="text-right">
          <span class="text-xs font-bold ${isHighRisk ? 'text-rose-400' : 'text-emerald-400'}">
            Risk: ${data.overall_fraud_score}% (${data.threat_level})
          </span>
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
        <div class="bg-dark-850 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-400 text-[10px]">Shortened Link?</span>
          <div class="font-semibold ${ui.is_shortener ? 'text-amber-400' : 'text-slate-200'}">
            ${ui.is_shortener ? 'Yes (Obfuscated)' : 'No (Direct Domain)'}
          </div>
        </div>
        <div class="bg-dark-850 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-400 text-[10px]">Free Form Provider?</span>
          <div class="font-semibold ${ui.is_form_host ? 'text-rose-400' : 'text-slate-200'}">
            ${ui.is_form_host ? 'Yes (Google/Typeform)' : 'No (Enterprise Host)'}
          </div>
        </div>
        <div class="bg-dark-850 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-400 text-[10px]">Content Crawl</span>
          <div class="font-semibold ${ui.fetch_success ? 'text-emerald-400' : 'text-slate-400'}">
            ${ui.fetch_success ? 'Successfully Extracted' : 'Unreachable / Restricted'}
          </div>
        </div>
      </div>

      ${ui.extracted_title ? `
        <div class="text-xs text-slate-300">
          <span class="text-slate-500">Page Title:</span> ${ui.extracted_title}
        </div>
      ` : ''}

      <!-- URL Flags List -->
      <div class="pt-2">
        <span class="text-xs font-semibold text-slate-300 block mb-1.5">Domain & Phishing Indicators:</span>
        <div class="space-y-1.5">
          ${(data.red_flags || []).map(f => `
            <div class="bg-dark-850 p-2 rounded-lg border border-slate-800 text-xs flex justify-between items-center">
              <span class="text-slate-300">${f.rule}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full ${f.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'}">${f.severity}</span>
            </div>
          `).join('')}
          ${(!data.red_flags || data.red_flags.length === 0) ? `
            <div class="text-xs text-emerald-400">Domain passed all phishing and reputation checks.</div>
          ` : ''}
        </div>
      </div>
    </div>
  `;
}

// ==========================================
// TAB 3: OFFER LETTER PDF VERIFIER
// ==========================================
function setupDragAndDrop() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("pdf-file-input");
  if (!dropZone || !fileInput) return;

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      handlePdfUpload({ target: fileInput });
    }
  });
}

async function handlePdfUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const resultBox = document.getElementById("doc-result-box");
  resultBox.innerHTML = `
    <div class="text-center py-10">
      <span class="animate-spin text-2xl inline-block mb-2">⚙️</span>
      <p class="text-xs text-slate-300 font-semibold">Extracting PDF text & inspecting clauses...</p>
    </div>
  `;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/analyze/document", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Document analysis failed");
    const data = await res.json();
    renderDocResult(data, file.name);

  } catch (err) {
    resultBox.innerHTML = `<div class="text-rose-400 text-xs p-4">Error: ${err.message}</div>`;
  }
}

async function testSamplePdf() {
  const resultBox = document.getElementById("doc-result-box");
  resultBox.innerHTML = `
    <div class="text-center py-10">
      <span class="animate-spin text-2xl inline-block mb-2">⚙️</span>
      <p class="text-xs text-slate-300 font-semibold">Loading and auditing sample PDF offer letter...</p>
    </div>
  `;

  try {
    const resp = await fetch("/samples/sample_fake_offer_letter.pdf");
    if (!resp.ok) throw new Error("Could not fetch sample PDF");
    const blob = await resp.blob();
    const file = new File([blob], "sample_fake_offer_letter.pdf", { type: "application/pdf" });

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/analyze/document", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Document analysis failed");
    const data = await res.json();
    renderDocResult(data, file.name);

  } catch (err) {
    resultBox.innerHTML = `<div class="text-rose-400 text-xs p-4">Error loading sample PDF: ${err.message}</div>`;
  }
}

function renderDocResult(data, filename) {
  const box = document.getElementById("doc-result-box");
  const isScam = data.overall_fraud_score >= 50;

  box.className = "bg-dark-850 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-4 text-left";
  box.innerHTML = `
    <div class="flex items-center justify-between pb-3 border-b border-slate-800">
      <div>
        <span class="text-[10px] text-slate-500 font-semibold uppercase">PDF Document Audited</span>
        <div class="text-sm font-bold text-white">${filename}</div>
      </div>
      <div class="text-right">
        <span class="text-xs font-bold ${isScam ? 'text-rose-400' : 'text-emerald-400'}">
          Fraud Score: ${data.overall_fraud_score}% (${data.threat_level})
        </span>
      </div>
    </div>

    <div class="p-3 bg-dark-900 rounded-xl border border-slate-800 text-xs text-slate-300">
      <span class="text-slate-500 block mb-1 font-semibold text-[10px] uppercase">Extracted Document Snippet:</span>
      <p class="font-mono text-[11px] leading-relaxed whitespace-pre-wrap">${data.extracted_snippet || 'No text extracted'}</p>
    </div>

    <div>
      <span class="text-xs font-semibold text-slate-300 block mb-1.5">Flagged Offer Letter Clauses:</span>
      <div class="space-y-1.5">
        ${(data.red_flags || []).map(f => `
          <div class="bg-dark-900 p-2.5 rounded-lg border border-slate-800 text-xs">
            <div class="flex justify-between items-center mb-1">
              <span class="font-semibold text-slate-200">${f.rule}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full ${f.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'}">${f.severity}</span>
            </div>
            <p class="text-[11px] text-slate-400">${f.detail}</p>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// ==========================================
// TAB 4: PLACEMENT CELL BULK AUDIT
// ==========================================
async function loadSampleBatchCsv() {
  const sampleCsv = `title,company,salary,contact_email,description
Software Development Engineer Intern,Amazon Web Services,$52/hour,aws-campus@amazon.com,AWS is hiring SWE Interns for S3. Build Go/Java microservices. Equal opportunity employer.
YouTube Video Liker & Reviewer,Global Media Review,INR 4000 daily,parttime.jobs@gmail.com,URGENT! Earn 4000 daily liking YouTube videos. UPI cash. Contact Telegram @MediaPayoutHR.
Graduate Engineer Trainee,Tata Consultancy Services,INR 4.5 LPA,campus.recruiting@tcs.com,TCS NQT drive for 2026 batch. TCS never charges any registration fee or deposit.
Data Entry Typist - Laptop Deposit Required,Apex Global,$60/hour,apex-jobs@yahoo.com,Earn 60/hr typing documents. Refundable security deposit of $150 required for laptop insurance.
Frontend React Engineer Intern,Vercel,$40/hour,careers@vercel.com,Design engineering team at Vercel. Develop Next.js and Tailwind components. TypeScript required.
Direct Selection Specialist (No Interview),Google LLC India,INR 14 LPA,google-recruiting@gmail.com,Direct appointment for Google without test. Pay verification charge of INR 2999.
Python Full Stack Intern (Mandatory Training Kit),TechVanguard,Unpaid / Fee INR 8500,techvanguard@gmail.com,6 months unpaid. Must buy industrial training kit worth 8500. Mandatory 2 year bond.
Cloud Operations Intern,Datadog,$45/hour,jobs@datadoghq.com,Maintain Kubernetes clusters and Prometheus alerts. Shell scripting and Linux fundamentals required.`;

  const blob = new Blob([sampleCsv], { type: "text/csv" });
  const file = new File([blob], "sample_placement_batch.csv");
  await executeBatchAudit(file);
}

async function handleBatchCsvUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  await executeBatchAudit(file);
}

async function executeBatchAudit(file) {
  const tbody = document.getElementById("batch-table-body");
  tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400"><span class="animate-spin inline-block mr-2">⚙️</span> Running Placement Audit on ${file.name}...</td></tr>`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/analyze/bulk", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Bulk audit failed");
    const data = await res.json();
    renderBatchResults(data);

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-rose-400">Error: ${err.message}</td></tr>`;
  }
}

function renderBatchResults(data) {
  document.getElementById("batch-metrics-bar").classList.remove("hidden");
  document.getElementById("batch-total").innerText = data.total_analyzed;
  document.getElementById("batch-flagged").innerText = data.high_risk_flagged;
  document.getElementById("batch-safe").innerText = data.verified_safe;
  document.getElementById("batch-ratio").innerText = `${data.clean_ratio}%`;

  const tbody = document.getElementById("batch-table-body");
  tbody.innerHTML = "";

  (data.listings || []).forEach(item => {
    const isScam = item.fraud_score >= 50;
    const badgeColor = isScam ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300';
    
    const tr = document.createElement("tr");
    tr.className = "hover:bg-dark-800/40 transition";
    tr.innerHTML = `
      <td class="p-3 font-mono text-slate-500">${item.id}</td>
      <td class="p-3 font-semibold text-white">${item.title}</td>
      <td class="p-3 text-slate-400">${item.company || 'N/A'}</td>
      <td class="p-3 font-mono font-bold ${isScam ? 'text-rose-400' : 'text-emerald-400'}">${item.fraud_score}%</td>
      <td class="p-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-semibold ${badgeColor}">${item.verdict}</span></td>
      <td class="p-3 text-slate-400">${item.primary_flag}</td>
      <td class="p-3 text-right">
        <button onclick="inspectBatchItem('${escape(JSON.stringify(item))}')" class="text-[11px] text-brand-400 hover:text-brand-300 underline">Details</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function inspectBatchItem(escapedJson) {
  try {
    const item = JSON.parse(unescape(escapedJson));
    alert(`Listing #${item.id}: ${item.title}\nCompany: ${item.company}\nFraud Score: ${item.fraud_score}%\nVerdict: ${item.verdict}\nKey Indicator: ${item.primary_flag}`);
  } catch (e) {
    console.error(e);
  }
}

// ==========================================
// TAB 5: SCAM INTEL DATABASE
// ==========================================
async function loadScams() {
  try {
    const res = await fetch("/api/scams");
    if (res.ok) {
      allScams = await res.json();
      renderScams(allScams);
    }
  } catch (err) {
    console.error("Failed to load scams:", err);
  }
}

function renderScams(scams) {
  const grid = document.getElementById("scam-cards-grid");
  if (!grid) return;
  grid.innerHTML = "";

  if (scams.length === 0) {
    grid.innerHTML = `<div class="col-span-3 text-center py-10 text-slate-500">No scams match your query.</div>`;
    return;
  }

  scams.forEach(item => {
    const card = document.createElement("div");
    card.className = "bg-dark-850 p-5 rounded-2xl border border-slate-800 space-y-3 shadow-lg hover:border-slate-700 transition";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-[10px] font-mono text-slate-500">${item.id}</span>
        <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ${item.threat_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'}">${item.threat_level}</span>
      </div>
      <div>
        <h3 class="text-sm font-bold text-white">${item.scam_type}</h3>
        <span class="text-xs text-brand-400">Claimed: ${item.company_claimed}</span>
      </div>
      <p class="text-xs text-slate-400 leading-relaxed">${item.modus_operandi}</p>
      <div class="flex flex-wrap gap-1 pt-1">
        ${(item.red_flags || []).map(rf => `<span class="text-[10px] px-2 py-0.5 rounded-md bg-dark-900 text-slate-300 border border-slate-800">${rf}</span>`).join('')}
      </div>
      <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
        <span>Target: ${item.target_audience}</span>
        <span>${item.reports_count} Reports</span>
      </div>
    `;
    grid.appendChild(card);
  });
}

function filterScams(query) {
  const q = query.toLowerCase();
  const filtered = allScams.filter(item => 
    item.scam_type.toLowerCase().includes(q) ||
    item.company_claimed.toLowerCase().includes(q) ||
    item.modus_operandi.toLowerCase().includes(q)
  );
  renderScams(filtered);
}

// Scam Reporting Modal
function openReportModal() {
  document.getElementById("report-modal").classList.remove("hidden");
}

function closeReportModal() {
  document.getElementById("report-modal").classList.add("hidden");
}

async function submitScamReport(e) {
  e.preventDefault();
  const payload = {
    scam_type: document.getElementById("report-type").value.trim(),
    company_claimed: document.getElementById("report-company").value.trim(),
    target_audience: document.getElementById("report-target").value.trim() || "College Students",
    modus_operandi: document.getElementById("report-desc").value.trim(),
    threat_level: document.getElementById("report-threat").value,
    red_flags: ["Community Flagged", "Advance Fee / Redirection"]
  };

  try {
    const res = await fetch("/api/scams", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      alert("Thank you! Your scam report has been added to the campus intelligence feed.");
      closeReportModal();
      loadScams();
    }
  } catch (err) {
    alert("Error submitting report: " + err.message);
  }
}

// ==========================================
// TAB 6: ACADEMIC METRICS & RESEARCH
// ==========================================
async function loadAcademicMetrics() {
  try {
    const res = await fetch("/api/model/metrics");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("metric-accuracy").innerText = `${(data.accuracy * 100).toFixed(1)}%`;
    document.getElementById("metric-precision").innerText = `${(data.precision * 100).toFixed(1)}%`;
    document.getElementById("metric-recall").innerText = `${(data.recall * 100).toFixed(1)}%`;
    document.getElementById("metric-f1").innerText = `${(data.f1_score * 100).toFixed(1)}%`;

    const cm = data.confusion_matrix || {};
    document.getElementById("cm-tn").innerText = cm.true_negatives || 0;
    document.getElementById("cm-fp").innerText = cm.false_positives || 0;
    document.getElementById("cm-fn").innerText = cm.false_negatives || 0;
    document.getElementById("cm-tp").innerText = cm.true_positives || 0;

    // Render Feature Chart
    if (typeof renderFeatureChart === "function") {
      renderFeatureChart(data.top_fraud_tokens, data.top_legit_tokens);
    }

  } catch (err) {
    console.error("Failed to load metrics:", err);
  }
}
