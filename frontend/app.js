// RecruitFlow AI - Frontend Application Logic

// Auto-detect API Base URL
const API_BASE = (window.location.protocol === 'file:') 
    ? 'http://127.0.0.1:8000' 
    : window.location.origin;

// State
let activeCandidate = 'rushi';
let activeTab = 'leads';
let statusFilter = 'all';
let searchQuery = '';
let searchDebounceTimer = null;
let candidatesData = {};
let jobsData = [];
let statsData = {};
let activeJobId = null;

// Initialize Dashboard on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    await checkApiHealth();
    await fetchCandidates();
    await loadAllCandidateStats();
    await loadStats();
    await loadJobs();
}

// ---------------- ALL CANDIDATE STATS & BREAKDOWN ---------------- //
async function loadAllCandidateStats() {
    try {
        const response = await fetch(`${API_BASE}/api/all-candidate-stats`);
        if (response.ok) {
            const data = await response.json();
            renderAllCandidateBreakdown(data.candidates);
        }
    } catch (err) {
        console.error("Error fetching all candidate stats:", err);
    }
}

function renderAllCandidateBreakdown(candidates) {
    const container = document.getElementById('allCandidatesBreakdownContainer');
    if (!container) return;

    const keys = Object.keys(candidates || {});
    if (keys.length === 0) {
        container.innerHTML = `<p class="text-xs text-slate-500">No candidate statistics available.</p>`;
        return;
    }

    container.innerHTML = keys.map(key => {
        const c = candidates[key];
        const pct = c.sent_percentage || 0;
        const isSelected = activeCandidate === key;

        let badgeBg = "bg-indigo-500/20 text-indigo-300 border-indigo-500/30";
        let iconClass = "fa-user-tie text-indigo-400";
        if (key === 'anoushika') {
            badgeBg = "bg-purple-500/20 text-purple-300 border-purple-500/30";
            iconClass = "fa-user-shield text-purple-400";
        } else if (key === 'default') {
            badgeBg = "bg-slate-800 text-slate-300 border-slate-700";
            iconClass = "fa-database text-slate-400";
        }

        return `
            <div class="bg-slate-950 p-4 rounded-xl border ${isSelected ? 'border-indigo-500 shadow-md shadow-indigo-500/10' : 'border-slate-800'} space-y-3 relative overflow-hidden group">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2.5">
                        <div class="w-9 h-9 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-base">
                            <i class="fa-solid ${iconClass}"></i>
                        </div>
                        <div>
                            <h4 class="text-sm font-bold text-white leading-tight">${escapeHtml(c.name)}</h4>
                            <p class="text-[11px] text-slate-400">${escapeHtml(c.db_file)}</p>
                        </div>
                    </div>
                    <span class="px-2 py-0.5 text-[10px] font-bold rounded border ${badgeBg}">
                        ${pct}% Sent
                    </span>
                </div>

                <div class="grid grid-cols-3 gap-2 py-1 text-center bg-slate-900/60 p-2 rounded-lg border border-slate-800/80 text-xs">
                    <div>
                        <span class="text-[10px] text-slate-500 block uppercase">Leads</span>
                        <span class="font-extrabold text-white">${c.total_recruiters.toLocaleString()}</span>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-500 block uppercase">Sent</span>
                        <span class="font-extrabold text-emerald-400">${c.emails_sent.toLocaleString()}</span>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-500 block uppercase">Pending</span>
                        <span class="font-extrabold text-amber-400">${c.pending.toLocaleString()}</span>
                    </div>
                </div>

                <div>
                    <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div class="bg-emerald-500 h-1.5 rounded-full" style="width: ${Math.min(pct, 100)}%"></div>
                    </div>
                </div>

                <div class="flex justify-between items-center pt-1 text-xs">
                    <span class="text-[11px] text-slate-500 truncate max-w-[150px]">${escapeHtml(c.work_auth || '')}</span>
                    <button onclick="focusCandidate('${key}')" class="text-xs font-semibold ${isSelected ? 'text-indigo-300 bg-indigo-500/20 px-2 py-0.5 rounded' : 'text-indigo-400 hover:text-indigo-300'} transition">
                        ${isSelected ? 'Active Filter ✓' : 'Focus View →'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function focusCandidate(key) {
    activeCandidate = key;
    document.getElementById('candidateSelect').value = key;
    handleCandidateChange();
}

// ---------------- API HEALTH CHECK ---------------- //
async function checkApiHealth() {
    const dot = document.getElementById('apiStatusDot');
    const text = document.getElementById('apiStatusText');
    try {
        const response = await fetch(`${API_BASE}/`);
        if (response.ok) {
            dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
            text.textContent = "API Connected";
            text.className = "text-emerald-400 font-medium";
        } else {
            throw new Error("API not ready");
        }
    } catch (err) {
        console.warn("API Health check failed:", err);
        dot.className = "w-2.5 h-2.5 rounded-full bg-amber-500";
        text.textContent = "Offline / Standalone";
        text.className = "text-amber-400 font-medium";
    }
}

// ---------------- FETCH CANDIDATES ---------------- //
async function fetchCandidates() {
    try {
        const response = await fetch(`${API_BASE}/api/candidates`);
        if (response.ok) {
            candidatesData = await response.json();
            renderCandidateProfiles();
            updateCampaignCandidateInfo();
        }
    } catch (err) {
        console.error("Error fetching candidates:", err);
    }
}

// ---------------- LOAD STATS ---------------- //
async function loadStats() {
    try {
        const url = `${API_BASE}/api/stats?client=${encodeURIComponent(activeCandidate)}`;
        const response = await fetch(url);
        if (response.ok) {
            statsData = await response.json();
            updateStatsUI(statsData);
        }
    } catch (err) {
        console.error("Error loading stats:", err);
    }
}

function updateStatsUI(stats) {
    document.getElementById('statTotal').textContent = stats.total_recruiters.toLocaleString() || '0';
    document.getElementById('statSent').textContent = stats.emails_sent.toLocaleString() || '0';
    document.getElementById('statPending').textContent = stats.pending.toLocaleString() || '0';
    
    const pct = stats.sent_percentage || 0;
    document.getElementById('statSentPercentage').textContent = `${pct}% Sent`;
    document.getElementById('statProgressBar').style.width = `${Math.min(pct, 100)}%`;
    document.getElementById('statDbLabel').innerHTML = `<i class="fa-solid fa-database text-indigo-400"></i> ${stats.db_file || 'all_databases'}`;
    document.getElementById('campaignPendingCount').textContent = stats.pending.toLocaleString() || '0';

    // Update candidate profile header card
    if (activeCandidate === 'all') {
        document.getElementById('statCandidateName').textContent = "All Candidates View";
        document.getElementById('statCandidateAuth').innerHTML = `<i class="fa-solid fa-layer-group text-purple-400 w-4"></i> Combined Pipeline`;
        document.getElementById('statCandidateLocation').innerHTML = `<i class="fa-solid fa-users text-purple-400 w-4"></i> Rushi & Anoushika`;
    } else {
        const currentCandidate = candidatesData[activeCandidate] || {};
        document.getElementById('statCandidateName').textContent = currentCandidate.name || (activeCandidate === 'anoushika' ? 'Santosh Anoushika' : 'Sai Rushi Kasyap');
        document.getElementById('statCandidateAuth').innerHTML = `<i class="fa-solid fa-shield-halved text-purple-400 w-4"></i> ${currentCandidate.work_auth || 'STEM OPT'}`;
        document.getElementById('statCandidateLocation').innerHTML = `<i class="fa-solid fa-location-dot text-purple-400 w-4"></i> ${currentCandidate.location || 'USA'}`;
    }
}

// ---------------- LOAD RECRUITER LEADS ---------------- //
async function loadJobs() {
    const tbody = document.getElementById('jobsTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="py-12 text-center text-slate-500">
                <i class="fa-solid fa-spinner fa-spin text-indigo-500 text-2xl mb-2"></i>
                <p>Loading recruiter leads...</p>
            </td>
        </tr>
    `;

    try {
        let queryParams = new URLSearchParams({
            client: activeCandidate,
            status: statusFilter,
            search: searchQuery,
            limit: 500
        });

        const response = await fetch(`${API_BASE}/api/jobs?${queryParams.toString()}`);
        if (!response.ok) throw new Error("Failed to load jobs");

        jobsData = await response.json();
        renderJobsTable(jobsData);
    } catch (err) {
        console.error("Error loading jobs:", err);
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="py-8 text-center text-rose-400">
                    <i class="fa-solid fa-circle-exclamation text-xl mb-1"></i>
                    <p>Failed to load recruiter leads from backend API.</p>
                </td>
            </tr>
        `;
        showToast("Error loading recruiter leads from API", "error");
    }
}

function renderJobsTable(jobs) {
    const tbody = document.getElementById('jobsTableBody');
    document.getElementById('tableShowingCount').textContent = jobs.length.toLocaleString();
    document.getElementById('tabCountLeads').textContent = jobs.length.toLocaleString();

    if (jobs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="py-12 text-center text-slate-500">
                    <i class="fa-solid fa-inbox text-3xl mb-2 text-slate-600"></i>
                    <p class="font-medium text-slate-400">No recruiter leads found</p>
                    <p class="text-xs text-slate-600 mt-1">Try adjusting your filter or search query</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = jobs.map(job => {
        const isSent = job.sent;
        const statusBadge = isSent 
            ? `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Sent
               </span>`
            : `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span> Pending
               </span>`;

        const candKey = job.candidate_id || job.client || activeCandidate;
        let candBadge = `<span class="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Sai Rushi</span>`;
        if (candKey === 'anoushika') {
            candBadge = `<span class="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">Anoushika</span>`;
        } else if (candKey === 'default') {
            candBadge = `<span class="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-slate-800 text-slate-300 border border-slate-700">Default DB</span>`;
        }

        const urlButton = job.url 
            ? `<a href="${escapeHtml(job.url)}" target="_blank" onclick="event.stopPropagation()" class="text-xs text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1">
                <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i> Link
               </a>`
            : `<span class="text-slate-600 text-xs">-</span>`;

        const keyword = job.search_keyword || 'LinkedIn Post';

        return `
            <tr onclick="openViewJobModal(${job.id})" class="cursor-pointer">
                <td class="py-3 px-4 whitespace-nowrap">${statusBadge}</td>
                <td class="py-3 px-4 whitespace-nowrap">${candBadge}</td>
                <td class="py-3 px-4 font-semibold text-slate-200">${escapeHtml(job.title || 'Untitled Lead')}</td>
                <td class="py-3 px-4 text-slate-300">${escapeHtml(job.company || 'Unknown Company')}</td>
                <td class="py-3 px-4 font-mono text-xs text-indigo-300">${escapeHtml(job.email || '')}</td>
                <td class="py-3 px-4 text-slate-400 text-xs">
                    <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60">${escapeHtml(keyword)}</span>
                </td>
                <td class="py-3 px-4 text-right space-x-2 whitespace-nowrap" onclick="event.stopPropagation()">
                    ${urlButton}
                    <button onclick="toggleJobSent(${job.id})" title="Toggle Sent/Pending" class="p-1.5 text-slate-400 hover:text-amber-400 bg-slate-800/80 hover:bg-slate-800 rounded-lg border border-slate-700 transition">
                        <i class="fa-solid fa-arrows-rotate text-xs"></i>
                    </button>
                    <button onclick="deleteJob(${job.id})" title="Delete Lead" class="p-1.5 text-slate-400 hover:text-rose-400 bg-slate-800/80 hover:bg-slate-800 rounded-lg border border-slate-700 transition">
                        <i class="fa-solid fa-trash-can text-xs"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// ---------------- TAB SWITCHING ---------------- //
function switchTab(tabName) {
    activeTab = tabName;
    
    // Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active', 'text-indigo-400', 'border-indigo-500');
        btn.classList.add('text-slate-400', 'border-transparent');
    });

    const activeBtn = document.getElementById(`tabBtn-${tabName}`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'text-indigo-400', 'border-indigo-500');
        activeBtn.classList.remove('text-slate-400', 'border-transparent');
    }

    // Panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.add('hidden');
    });

    const activePanel = document.getElementById(`tabContent-${tabName}`);
    if (activePanel) {
        activePanel.classList.remove('hidden');
    }
}

// ---------------- FILTERING & CANDIDATE SELECT ---------------- //
function setStatusFilter(filter) {
    statusFilter = filter;
    ['all', 'unsent', 'sent'].forEach(f => {
        const btn = document.getElementById(`filterBtn-${f}`);
        if (f === filter) {
            btn.className = "px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white shadow";
        } else {
            btn.className = "px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-400 hover:text-white";
        }
    });
    loadJobs();
}

function handleSearchInput() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        searchQuery = document.getElementById('searchInput').value;
        loadJobs();
    }, 300);
}

function handleCandidateChange() {
    activeCandidate = document.getElementById('candidateSelect').value;
    updateCampaignCandidateInfo();
    loadStats();
    loadJobs();
}

function updateCampaignCandidateInfo() {
    const candidate = candidatesData[activeCandidate] || {};
    const name = candidate.name || (activeCandidate === 'anoushika' ? 'Santosh Anoushika Komala' : 'Sai Rushi Kasyap');
    const auth = candidate.work_auth ? `${candidate.keywords?.[0] || 'Outreach'} • ${candidate.work_auth}` : 'Outreach Profile';
    
    document.getElementById('campaignCandidateName').textContent = name;
    document.getElementById('campaignCandidateAuth').textContent = auth;
    document.getElementById('campaignResumeName').textContent = candidate.base_resume_pdf || 'Resumes.pdf';
}

// ---------------- ADD JOB MODAL ---------------- //
function openAddJobModal() {
    document.getElementById('addModalClient').value = activeCandidate;
    document.getElementById('addJobModal').classList.remove('hidden');
}

function closeAddJobModal() {
    document.getElementById('addJobModal').classList.add('hidden');
    document.getElementById('addJobForm').reset();
}

async function handleAddJobSubmit(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById('addModalTitle').value.trim(),
        company: document.getElementById('addModalCompany').value.trim(),
        email: document.getElementById('addModalEmail').value.trim(),
        url: document.getElementById('addModalUrl').value.trim(),
        job_description: document.getElementById('addModalDesc').value.trim(),
        client: document.getElementById('addModalClient').value
    };

    try {
        const response = await fetch(`${API_BASE}/api/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            showToast("Recruiter job lead added successfully!", "success");
            closeAddJobModal();
            await loadStats();
            await loadJobs();
        } else {
            showToast(data.detail || "Failed to add lead", "error");
        }
    } catch (err) {
        console.error("Error adding job:", err);
        showToast("Server error when adding lead", "error");
    }
}

// ---------------- VIEW JOB MODAL ---------------- //
async function openViewJobModal(jobId) {
    activeJobId = jobId;
    const modal = document.getElementById('viewJobModal');
    modal.classList.remove('hidden');

    document.getElementById('viewJobTitle').textContent = "Loading...";
    document.getElementById('viewJobCompany').textContent = "";
    document.getElementById('viewJobEmail').textContent = "";
    document.getElementById('viewJobDesc').textContent = "Fetching details...";

    try {
        const response = await fetch(`${API_BASE}/api/jobs/${jobId}?client=${encodeURIComponent(activeCandidate)}`);
        if (!response.ok) throw new Error("Failed to load details");
        const job = await response.json();

        document.getElementById('viewJobTitle').textContent = job.title || 'Untitled Lead';
        document.getElementById('viewJobCompany').textContent = job.company || 'Unknown Company';
        document.getElementById('viewJobEmail').textContent = job.email || '';
        document.getElementById('viewJobDesc').textContent = job.job_description || 'No description available for this lead.';

        const urlElem = document.getElementById('viewJobUrl');
        if (job.url) {
            urlElem.href = job.url;
            urlElem.textContent = job.url;
            urlElem.style.display = 'block';
        } else {
            urlElem.style.display = 'none';
        }

        const badge = document.getElementById('viewJobStatusBadge');
        if (job.sent) {
            badge.className = "inline-block text-[11px] font-bold px-2.5 py-0.5 rounded-full mb-1 bg-emerald-500/20 text-emerald-300";
            badge.textContent = "Sent";
        } else {
            badge.className = "inline-block text-[11px] font-bold px-2.5 py-0.5 rounded-full mb-1 bg-amber-500/20 text-amber-300";
            badge.textContent = "Pending Outreach";
        }

    } catch (err) {
        console.error("Error opening job detail:", err);
        showToast("Error loading job details", "error");
    }
}

function closeViewJobModal() {
    document.getElementById('viewJobModal').classList.add('hidden');
    activeJobId = null;
}

async function toggleCurrentJobSent() {
    if (!activeJobId) return;
    await toggleJobSent(activeJobId);
    openViewJobModal(activeJobId);
}

async function toggleJobSent(jobId) {
    try {
        const response = await fetch(`${API_BASE}/api/jobs/${jobId}/toggle-sent?client=${encodeURIComponent(activeCandidate)}`, {
            method: 'PATCH'
        });
        if (response.ok) {
            showToast("Updated lead sent status", "info");
            await loadStats();
            await loadJobs();
        }
    } catch (err) {
        console.error("Error toggling sent status:", err);
        showToast("Failed to update status", "error");
    }
}

async function deleteJob(jobId) {
    if (!confirm("Are you sure you want to delete this recruiter lead?")) return;

    try {
        const response = await fetch(`${API_BASE}/api/jobs/${jobId}?client=${encodeURIComponent(activeCandidate)}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            showToast("Lead deleted successfully", "success");
            await loadStats();
            await loadJobs();
        } else {
            showToast("Failed to delete lead", "error");
        }
    } catch (err) {
        console.error("Error deleting job:", err);
        showToast("Server error during deletion", "error");
    }
}

// ---------------- CAMPAIGN RUNNER ---------------- //
function updateBatchLimitDisplay(val) {
    document.getElementById('limitDisplayValue').textContent = `${val} emails`;
}

function appendConsoleLog(text, type = 'info') {
    const consoleBox = document.getElementById('campaignConsole');
    const timestamp = new Date().toLocaleTimeString();
    let colorClass = 'text-slate-300';
    if (type === 'success') colorClass = 'text-emerald-400 font-semibold';
    if (type === 'error') colorClass = 'text-rose-400 font-semibold';
    if (type === 'warn') colorClass = 'text-amber-400';

    const line = document.createElement('div');
    line.className = colorClass;
    line.innerHTML = `<span class="text-slate-600">[${timestamp}]</span> ${escapeHtml(text)}`;
    consoleBox.appendChild(line);
    consoleBox.scrollTop = consoleBox.scrollHeight;
}

function clearConsoleLog() {
    document.getElementById('campaignConsole').innerHTML = `<div class="text-slate-500">// Console cleared.</div>`;
}

async function executeCampaign() {
    const limit = parseInt(document.getElementById('batchLimitSlider').value, 10);
    const btn = document.getElementById('btnStartCampaign');
    const badge = document.getElementById('campaignStatusBadge');

    if (!confirm(`Launch automated email outreach campaign for ${activeCandidate.toUpperCase()} (Batch Limit: ${limit} emails)?`)) {
        return;
    }

    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running Outreach Campaign...`;
    badge.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-ping"></span> <span class="text-indigo-400 font-bold">Campaign In Progress</span>`;

    appendConsoleLog(`Initiating automated email outreach batch (${limit} recipients)...`, 'info');
    appendConsoleLog(`Candidate selected: ${activeCandidate}`, 'info');

    try {
        const response = await fetch(`${API_BASE}/api/send-emails`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client_id: activeCandidate,
                limit: limit
            })
        });

        const data = await response.json();

        if (response.ok) {
            appendConsoleLog(`✓ Campaign Batch Execution Completed Successfully!`, 'success');
            appendConsoleLog(`Message: ${data.message || 'Outreach completed.'}`, 'success');
            showToast("Outreach campaign executed successfully!", "success");

            // Celebrate with confetti!
            if (typeof confetti === 'function') {
                confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
            }
        } else {
            appendConsoleLog(`✗ Campaign Error: ${data.detail || 'Execution failed'}`, 'error');
            showToast(data.detail || "Campaign failed", "error");
        }

        await loadStats();
        await loadJobs();

    } catch (err) {
        console.error("Campaign execution error:", err);
        appendConsoleLog(`✗ System Network Error: ${err.message}`, 'error');
        showToast("Failed to connect to outreach server", "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Start Automated Campaign`;
        badge.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> <span class="text-emerald-400">Campaign Completed</span>`;
    }
}

// ---------------- CANDIDATE PROFILES RENDERER ---------------- //
function renderCandidateProfiles() {
    const container = document.getElementById('candidateProfilesContainer');
    if (!container) return;

    const keys = Object.keys(candidatesData);
    if (keys.length === 0) {
        container.innerHTML = `<p class="text-slate-400">No profiles found.</p>`;
        return;
    }

    container.innerHTML = keys.map(key => {
        const c = candidatesData[key];
        const keywords = c.keywords || [];

        const keywordsPills = keywords.map(k => 
            `<span class="px-2.5 py-1 bg-indigo-500/10 text-indigo-300 text-[11px] font-medium rounded-lg border border-indigo-500/20">${escapeHtml(k)}</span>`
        ).join(' ');

        const eduList = (c.education || []).map(edu => 
            `<div class="text-xs text-slate-300">
                <span class="font-bold text-white">${escapeHtml(edu.degree || '')}</span>
                <span class="text-slate-400"> - ${escapeHtml(edu.institution || '')} (${escapeHtml(edu.duration || '')})</span>
             </div>`
        ).join('');

        return `
            <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div>
                        <h3 class="text-lg font-bold text-white">${escapeHtml(c.name || key)}</h3>
                        <p class="text-xs text-indigo-400 font-semibold">${escapeHtml(c.email || '')} • ${escapeHtml(c.phone || '')}</p>
                    </div>
                    <span class="px-3 py-1 bg-purple-500/20 text-purple-300 text-xs font-bold rounded-full border border-purple-500/30">
                        ${escapeHtml(c.work_auth || 'Visa Authorized')}
                    </span>
                </div>

                <div class="grid grid-cols-2 gap-3 text-xs">
                    <div>
                        <span class="text-slate-500">Location:</span>
                        <p class="font-medium text-slate-200">${escapeHtml(c.location || 'USA')}</p>
                    </div>
                    <div>
                        <span class="text-slate-500">Availability:</span>
                        <p class="font-medium text-slate-200">${escapeHtml(c.availability || 'Immediate')}</p>
                    </div>
                </div>

                <div>
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Education</span>
                    ${eduList || '<p class="text-xs text-slate-500">No education listed</p>'}
                </div>

                <div>
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Target Skills & Role Keywords</span>
                    <div class="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-1">
                        ${keywordsPills}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ---------------- PREVIEW GENERATOR ---------------- //
async function generatePreviewEmail() {
    const candidateId = document.getElementById('previewCandidate').value;
    const title = document.getElementById('previewJobTitle').value;
    const company = document.getElementById('previewCompany').value;
    const desc = document.getElementById('previewJobDesc').value;
    const outputElem = document.getElementById('previewEmailOutput');

    outputElem.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-indigo-400"></i> Tailoring resume & generating email preview...`;

    try {
        const response = await fetch(`${API_BASE}/api/preview-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client_id: candidateId,
                job_title: title,
                company: company,
                job_description: desc
            })
        });

        const data = await response.json();
        if (response.ok) {
            outputElem.textContent = data.email_preview || "Preview generated.";
            document.getElementById('previewCandidateBadge').textContent = `Preview for ${data.candidate || candidateId}`;
        } else {
            outputElem.textContent = `Error: ${data.detail || 'Failed to generate preview'}`;
        }
    } catch (err) {
        console.error("Preview error:", err);
        outputElem.textContent = "Error connecting to preview API.";
    }
}

// ---------------- TOAST NOTIFICATIONS ---------------- //
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    
    let borderClass = 'border-indigo-500/50 bg-slate-900/95 text-slate-200';
    let iconClass = 'fa-info-circle text-indigo-400';
    
    if (type === 'success') {
        borderClass = 'border-emerald-500/50 bg-slate-900/95 text-emerald-200';
        iconClass = 'fa-circle-check text-emerald-400';
    } else if (type === 'error') {
        borderClass = 'border-rose-500/50 bg-slate-900/95 text-rose-200';
        iconClass = 'fa-circle-xmark text-rose-400';
    }

    toast.className = `toast pointer-events-auto flex items-center space-x-3 px-4 py-3 rounded-xl border shadow-2xl text-xs font-semibold ${borderClass}`;
    toast.innerHTML = `<i class="fa-solid ${iconClass} text-base"></i> <span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ---------------- UTILS ---------------- //
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}