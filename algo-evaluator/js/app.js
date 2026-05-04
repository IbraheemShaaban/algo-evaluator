/**
 * app.js — Main Application Controller
 * Ties together Engine, Classifier, ChartManager, and the UI.
 */

// ============================================================
// STATE
// ============================================================
let currentMode = 'manual';
let lastResults = null;
window._stopRequested = false;

// ============================================================
// MODE SWITCHING
// ============================================================
function setMode(mode) {
  currentMode = mode;
  document.getElementById('btn-manual').classList.toggle('active', mode === 'manual');
  document.getElementById('btn-auto').classList.toggle('active', mode === 'auto');
  document.getElementById('manual-section').classList.toggle('hidden', mode !== 'manual');
  document.getElementById('auto-section').classList.toggle('hidden', mode !== 'auto');
  document.getElementById('status-mode').textContent =
    mode === 'manual' ? 'Manual Mode' : 'Auto Mode';
  setStatus(mode === 'manual'
    ? 'Manual mode — enter an array and run your algorithm'
    : 'Auto mode — configure test sizes and run comprehensive analysis');
}

// ============================================================
// RUN ANALYSIS
// ============================================================
async function runAnalysis() {
  hideError();
  const userCode = document.getElementById('code-editor').value.trim();

  if (!userCode) {
    showError('Please write some algorithm code first.');
    return;
  }

  // Test the syntax upfront
  const built = Engine.buildFunction(userCode);
  if (!built.ok) {
    showError('Syntax Error: ' + built.error);
    return;
  }

  setRunning(true);
  window._stopRequested = false;
  ChartManager.clear();
  resetResults();

  let result;

  if (currentMode === 'manual') {
    const arrayStr = document.getElementById('manual-array').value;
    result = await Engine.runManual(
      userCode,
      arrayStr,
      5,
      (pct, label) => updateProgress(pct, label)
    );
  } else {
    const config = getAutoConfig();
    result = await Engine.runAuto(
      userCode,
      config,
      (pct, label) => updateProgress(pct, label)
    );
  }

  setRunning(false);

  if (!result.ok) {
    showError(result.error);
    setStatus('Analysis failed — check the error above');
    return;
  }

  if (!result.measurements || result.measurements.length === 0) {
    showError('No measurements collected. Try a larger input or check your code.');
    return;
  }

  lastResults = result.measurements;
  processAndDisplay(result.measurements, result.stopped);
}

// ============================================================
// PROCESS & DISPLAY RESULTS
// ============================================================
function processAndDisplay(measurements, stopped) {
  const classified = Classifier.classifyByType(measurements);
  const overall = Classifier.overallBest(classified);

  // Render chart
  ChartManager.render(classified);

  // Display complexity
  displayComplexity(classified, overall);

  // Render table
  renderTable(measurements);

  const suffix = stopped ? ' (stopped early)' : '';
  setStatus(`Analysis complete${suffix} — ${measurements.length} measurements collected`);
}

// ============================================================
// COMPLEXITY DISPLAY
// ============================================================
function displayComplexity(classified, overall) {
  document.getElementById('complexity-empty').classList.add('hidden');
  const result = document.getElementById('complexity-result');
  result.classList.remove('hidden');

  const badgesRow = document.getElementById('complexity-badges-row');
  const statsRow = document.getElementById('complexity-stats-row');
  badgesRow.innerHTML = '';
  statsRow.innerHTML = '';

  // Main badge
  if (overall) {
    const main = document.createElement('div');
    main.className = 'complexity-main-badge';
    main.style.color = overall.color;
    main.style.borderColor = overall.color;
    main.style.background = overall.color + '15';
    main.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <path d="M2 14 Q6 8 9 6 Q12 4 16 2" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
      </svg>
      ${overall.label}
      <span style="font-size:13px;opacity:0.7;font-weight:500">${overall.name}</span>
    `;
    badgesRow.appendChild(main);
  }

  // Per-type badges
  for (const [type, data] of Object.entries(classified)) {
    if (!data.best) continue;
    const badge = document.createElement('div');
    badge.className = `complexity-case-badge badge-${type === 'manual' ? 'random' : type}`;
    badge.innerHTML = `
      <span style="opacity:0.7;font-size:11px;">${typeLabelShort(type)}:</span>
      <span>${data.best.label}</span>
      <span style="opacity:0.6;font-size:11px;">R²=${data.best.r2.toFixed(3)}</span>
    `;
    badgesRow.appendChild(badge);
  }

  // Stats cards
  if (overall) {
    const r2Class = overall.r2 >= 0.95 ? 'good' : overall.r2 >= 0.80 ? 'ok' : 'bad';
    addStatCard(statsRow, 'Best Fit', overall.label, '');
    addStatCard(statsRow, 'R² Score', overall.r2.toFixed(4), r2Class);
    addStatCard(statsRow, 'Confidence', pct(overall.r2), r2Class);
    addStatCard(statsRow, 'Class', overall.name, '');
  }

  // Candidates (top 3)
  const best = Object.values(classified)[0];
  if (best && best.candidates && best.candidates.length > 1) {
    const topN = best.candidates.slice(0, 3);
    for (const c of topN) {
      addStatCard(statsRow, c.label, `R²=${c.r2.toFixed(3)}`, '');
    }
  }
}

function typeLabelShort(type) {
  return { random: 'avg', sorted: 'best', reverse: 'worst', manual: 'manual' }[type] || type;
}

function pct(r2) {
  return Math.round(r2 * 100) + '%';
}

function addStatCard(row, label, value, cls) {
  const card = document.createElement('div');
  card.className = 'stat-card';
  card.innerHTML = `
    <div class="stat-label">${label}</div>
    <div class="stat-value ${cls}">${value}</div>
  `;
  row.appendChild(card);
}

// ============================================================
// TABLE
// ============================================================
function renderTable(measurements) {
  const wrap = document.getElementById('table-wrap');
  if (!measurements || measurements.length === 0) {
    wrap.innerHTML = '<div class="table-empty">No measurements yet.</div>';
    return;
  }

  const sorted = [...measurements].sort((a, b) => {
    const typeOrder = ['manual','random','sorted','reverse'];
    const ta = typeOrder.indexOf(a.type), tb = typeOrder.indexOf(b.type);
    if (ta !== tb) return ta - tb;
    return a.size - b.size;
  });

  let rows = sorted.map(m => `
    <tr>
      <td class="td-size">${m.size.toLocaleString()}</td>
      <td class="td-type">${typeLabelShort(m.type)}</td>
      <td class="td-time">${ChartManager.formatTime(m.time)}</td>
      <td class="td-time" style="opacity:0.6">${(m.time * 1000).toFixed(1)} μs</td>
    </tr>
  `).join('');

  wrap.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Input Size (n)</th>
          <th>Case</th>
          <th>Avg Time</th>
          <th>Microseconds</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// ============================================================
// AUTO CONFIG
// ============================================================
function getAutoConfig() {
  const preset = document.getElementById('size-preset').value;
  const runs = parseInt(document.getElementById('runs-per-size').value);

  let sizes;
  if (preset === 'small')       sizes = [10, 50, 100, 200, 500];
  else if (preset === 'medium') sizes = [100, 500, 1000, 2000, 5000];
  else if (preset === 'large')  sizes = [1000, 5000, 10000, 20000, 50000];
  else {
    const custom = document.getElementById('custom-sizes').value;
    sizes = custom.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n > 0);
    if (sizes.length === 0) sizes = [100, 500, 1000, 2000, 5000];
  }

  const types = [];
  if (document.getElementById('cb-random').checked)  types.push('random');
  if (document.getElementById('cb-sorted').checked)  types.push('sorted');
  if (document.getElementById('cb-reverse').checked) types.push('reverse');
  if (types.length === 0) types.push('random');

  return { sizes, runs, types };
}

// ============================================================
// QUICK ARRAY GENERATORS
// ============================================================
function quickArray(n, type) {
  const arr = Engine.generateArray(n, type);
  document.getElementById('manual-array').value = arr.join(', ');
}

// ============================================================
// EXAMPLE LOADERS
// ============================================================
function loadExample(name) {
  const examples = {
    bubble: `// O(n²) — Bubble Sort
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        let tmp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = tmp;
      }
    }
  }
  return arr;`,

    merge: `// O(n log n) — Merge Sort
  function merge(left, right) {
    let result = [], i = 0, j = 0;
    while (i < left.length && j < right.length) {
      if (left[i] <= right[j]) result.push(left[i++]);
      else result.push(right[j++]);
    }
    return result.concat(left.slice(i)).concat(right.slice(j));
  }
  function mergeSort(a) {
    if (a.length <= 1) return a;
    const mid = Math.floor(a.length / 2);
    return merge(mergeSort(a.slice(0, mid)), mergeSort(a.slice(mid)));
  }
  return mergeSort(arr);`,

    linear: `// O(n) — Linear Search
  let target = Math.floor(arr.length / 2);
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] === target) return i;
  }
  return -1;`,
  };

  if (examples[name]) {
    document.getElementById('code-editor').value = examples[name];
  }
}

function clearEditor() {
  document.getElementById('code-editor').value = '';
}

// ============================================================
// STOP
// ============================================================
function stopAnalysis() {
  window._stopRequested = true;
  setStatus('Stopping…');
}

// ============================================================
// CHART CONTROLS
// ============================================================
function setChartScale(scale) {
  ChartManager.setScale(scale);
  document.getElementById('chart-linear-btn').classList.toggle('active', scale === 'linear');
  document.getElementById('chart-log-btn').classList.toggle('active', scale === 'log');
}

function exportChart() {
  ChartManager.exportPng();
}

// ============================================================
// UI HELPERS
// ============================================================
function setRunning(running) {
  const btn = document.getElementById('run-btn');
  const stopBtn = document.getElementById('stop-btn');
  const progressWrap = document.getElementById('progress-wrap');

  btn.disabled = running;
  document.getElementById('run-btn-text').textContent = running ? 'Running…' : 'Run Analysis';
  stopBtn.classList.toggle('hidden', !running);
  progressWrap.classList.toggle('hidden', !running);

  if (!running) {
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-label').textContent = '';
  }
}

function updateProgress(pct, label) {
  document.getElementById('progress-bar').style.width = (pct * 100) + '%';
  document.getElementById('progress-label').textContent = label || 'Running…';
}

function showError(msg) {
  const box = document.getElementById('error-box');
  document.getElementById('error-msg').textContent = msg;
  box.classList.remove('hidden');
}

function hideError() {
  document.getElementById('error-box').classList.add('hidden');
}

function setStatus(msg) {
  document.getElementById('status-msg').textContent = msg;
}

function resetResults() {
  document.getElementById('complexity-empty').classList.remove('hidden');
  document.getElementById('complexity-result').classList.add('hidden');
  document.getElementById('table-wrap').innerHTML = '<div class="table-empty">No measurements yet. Run an analysis first.</div>';
}

// ============================================================
// AUTO-CONFIG SHOW/HIDE CUSTOM SIZES
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('size-preset').addEventListener('change', function() {
    const customItem = document.getElementById('custom-sizes-item');
    if (customItem) customItem.style.display = this.value === 'custom' ? '' : 'none';
  });

  setStatus('Ready — select a mode and write your algorithm');
});
