const form = document.getElementById("screeningForm");
const jobDescription = document.getElementById("jobDescription");
const resumes = document.getElementById("resumes");
const rankButton = document.getElementById("rankButton");
const statusMessage = document.getElementById("statusMessage");
const topCandidates = document.getElementById("topCandidates");
const rankingTable = document.getElementById("rankingTable");
const errorList = document.getElementById("errorList");
const API_BASE_URL = window.location.protocol === "file:" || window.location.port === "5500"
  ? "http://127.0.0.1:8000"
  : "";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessages();

  if (!jobDescription.value.trim()) {
    setStatus("Please enter a job description.", true);
    return;
  }

  if (!resumes.files.length) {
    setStatus("Please upload at least one resume.", true);
    return;
  }

  const formData = new FormData();
  formData.append("job_description", jobDescription.value.trim());

  Array.from(resumes.files).forEach((file) => {
    formData.append("resumes", file);
  });

  rankButton.disabled = true;
  setStatus("Screening resumes...");

  try {
    const response = await fetch(`${API_BASE_URL}/api/rank`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      const message = typeof data.detail === "string"
        ? data.detail
        : data.detail?.message || "Unable to process resumes.";
      throw new Error(message);
    }

    renderTopCandidates(data.top_candidates || []);
    renderRankingTable(data.candidates || []);
    renderErrors(data.errors || []);
    setStatus(`Processed ${data.total_processed} resume(s).`);
  } catch (error) {
    setStatus(error.message, true);
    renderTopCandidates([]);
    renderRankingTable([]);
  } finally {
    rankButton.disabled = false;
  }
});

function renderTopCandidates(candidates) {
  if (!candidates.length) {
    topCandidates.className = "top-candidates empty-state";
    topCandidates.textContent = "Results will appear after screening.";
    return;
  }

  topCandidates.className = "top-candidates";
  topCandidates.innerHTML = candidates.map((candidate) => `
    <article class="candidate-card">
      <span class="rank-pill">#${candidate.rank}</span>
      <h3>${escapeHtml(candidate.candidate_name)}</h3>
      <div class="score">${candidate.score}%</div>
      <p class="meta-line">${escapeHtml(candidate.experience)}</p>
      ${renderChips(candidate.skills.slice(0, 6))}
    </article>
  `).join("");
}

function renderRankingTable(candidates) {
  if (!candidates.length) {
    rankingTable.innerHTML = '<tr><td colspan="5" class="empty-table">No candidates ranked yet.</td></tr>';
    return;
  }

  rankingTable.innerHTML = candidates.map((candidate) => `
    <tr>
      <td><strong>#${candidate.rank}</strong></td>
      <td>
        <strong>${escapeHtml(candidate.candidate_name)}</strong>
        <div class="meta-line">${escapeHtml(candidate.file_name)}</div>
      </td>
      <td>
        <strong>${candidate.score}%</strong>
        <div class="score-bar"><span style="width: ${Math.min(candidate.score, 100)}%"></span></div>
      </td>
      <td>${escapeHtml(candidate.experience)}</td>
      <td>${renderChips(candidate.matched_keywords.slice(0, 10))}</td>
    </tr>
  `).join("");
}

function renderErrors(errors) {
  if (!errors.length) {
    errorList.innerHTML = "";
    return;
  }

  errorList.innerHTML = errors.map((item) => `
    <div class="error-item">
      <strong>${escapeHtml(item.file || "File")}:</strong> ${escapeHtml(item.error)}
    </div>
  `).join("");
}

function renderChips(items) {
  if (!items || !items.length) {
    return '<div class="chips"><span class="chip">No keywords found</span></div>';
  }

  return `<div class="chips">${items.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div>`;
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.style.color = isError ? "#b42318" : "#65717b";
}

function clearMessages() {
  setStatus("");
  errorList.innerHTML = "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
