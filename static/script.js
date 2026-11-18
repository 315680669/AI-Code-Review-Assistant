const analyseButton = document.getElementById("analyseButton");
const codeInput = document.getElementById("codeInput");
const emptyState = document.getElementById("emptyState");
const resultsContent = document.getElementById("resultsContent");
const resultBadge = document.getElementById("resultBadge");
const HISTORY_KEY = "codeReviewDecisionHistory";
let latestAnalysis = null;

function renderChecks(checks) {
  const list = document.getElementById("checksList");
  list.replaceChildren();
  checks.forEach(check => {
    const card = document.createElement("div");
    card.className = "check-card";
    const heading = document.createElement("div");
    heading.className = "check-heading";
    const name = document.createElement("strong");
    name.textContent = check.name;
    const result = document.createElement("span");
    result.className = "check-result";
    result.textContent = check.result;
    heading.append(name, result);
    const details = document.createElement("p");
    details.textContent = `Input: ${check.input} · Expected: ${check.expected}`;
    const note = document.createElement("p");
    note.className = "muted small";
    note.textContent = check.detail;
    card.append(heading, details, note);
    list.appendChild(card);
  });
}

function renderHistory() {
  const historyList = document.getElementById("historyList");
  const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  historyList.replaceChildren();
  if (!history.length) {
    const empty = document.createElement("p");
    empty.className = "muted small";
    empty.textContent = "No decisions recorded yet.";
    historyList.appendChild(empty);
    return;
  }
  history.slice().reverse().forEach(entry => {
    const item = document.createElement("div");
    item.className = "history-item";
    const top = document.createElement("div");
    top.className = "check-heading";
    const decision = document.createElement("strong");
    decision.textContent = entry.decision;
    const time = document.createElement("span");
    time.className = "muted small";
    time.textContent = new Date(entry.time).toLocaleString();
    top.append(decision, time);
    const summary = document.createElement("p");
    summary.textContent = entry.summary;
    const snippet = document.createElement("code");
    snippet.textContent = entry.codePreview;
    item.append(top, summary, snippet);
    historyList.appendChild(item);
  });
}

analyseButton.addEventListener("click", async () => {
  analyseButton.disabled = true;
  analyseButton.textContent = "Analysing...";
  document.getElementById("decisionMessage").textContent = "";
  try {
    const response = await fetch("/analyse", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({code: codeInput.value})
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not analyse the code.");
    latestAnalysis = result;
    document.getElementById("explanationText").textContent = result.explanation;
    document.getElementById("testStatus").textContent = result.test_status;
    document.getElementById("testStatus").className = "test-status" +
      (result.issues.length ? "" : " pass");
    document.getElementById("summaryText").textContent = result.summary;
    renderChecks(result.checks || []);

    const issuesList = document.getElementById("issuesList");
    issuesList.replaceChildren();
    if (!result.issues.length) {
      const message = document.createElement("p");
      message.className = "no-issues";
      message.textContent = "No issues detected by the current checks.";
      issuesList.appendChild(message);
    } else {
      result.issues.forEach(issue => {
        const item = document.createElement("div");
        item.className = "issue" + (issue.severity === "warning" ? " warning" : "");
        const title = document.createElement("strong");
        title.textContent = issue.title;
        const detail = document.createElement("span");
        detail.textContent = issue.detail;
        item.append(title, detail);
        issuesList.appendChild(item);
      });
    }
    resultBadge.textContent = result.status;
    resultBadge.className = "result-badge " + (result.issues.length ? "error" : "ok");
    emptyState.classList.add("hidden");
    resultsContent.classList.remove("hidden");
  } catch (error) {
    alert(error.message);
  } finally {
    analyseButton.disabled = false;
    analyseButton.innerHTML = 'Analyse code <span>→</span>';
  }
});

document.querySelectorAll("[data-decision]").forEach(button => {
  button.addEventListener("click", () => {
    if (!latestAnalysis) {
      document.getElementById("decisionMessage").textContent = "Analyse the code before recording a decision.";
      return;
    }
    const decision = button.dataset.decision;
    const messages = {
      "Accepted": "Decision recorded: you accepted this suggestion. Basic checks do not guarantee correctness.",
      "Rejected": "Decision recorded: you rejected this suggestion.",
      "Needs editing": "Decision recorded: you want to edit this suggestion. Update the code and analyse it again."
    };
    const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    history.push({
      decision,
      time: new Date().toISOString(),
      summary: latestAnalysis.summary,
      codePreview: codeInput.value.trim().slice(0, 180) || "(empty code)"
    });
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-30)));
    document.getElementById("decisionMessage").textContent = messages[decision];
    renderHistory();
    if (decision === "Needs editing") {
      codeInput.focus();
      codeInput.scrollIntoView({behavior: "smooth", block: "center"});
    }
  });
});

document.getElementById("clearHistoryButton").addEventListener("click", () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
});

renderHistory();
