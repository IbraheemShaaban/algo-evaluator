/**
 * chart-manager.js — Chart.js integration for plotting results
 */

window.ChartManager = (() => {
  let chartInstance = null;
  let currentScale = 'linear';
  let lastClassifiedData = null;

  const TYPE_COLORS = {
    random:  '#00d4ff',
    sorted:  '#22c55e',
    reverse: '#ffd166',
    manual:  '#3fefb4',
  };

  const TYPE_LABELS = {
    random:  'Random (avg case)',
    sorted:  'Sorted (best case)',
    reverse: 'Reversed (worst case)',
    manual:  'Manual Input',
  };

  function getCtx() {
    return document.getElementById('main-chart');
  }

  function showChart() {
    const canvas = getCtx();
    const empty = document.getElementById('chart-empty');
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';
  }

  /**
   * Render chart from classified data.
   * classifiedByType: { type: { measurements, best } }
   */
  function render(classifiedByType) {
    lastClassifiedData = classifiedByType;
    showChart();

    const allSizes = new Set();
    for (const data of Object.values(classifiedByType)) {
      data.measurements.forEach(m => allSizes.add(m.size));
    }
    const sizes = [...allSizes].sort((a, b) => a - b);

    const datasets = [];

    // Measurement datasets
    for (const [type, data] of Object.entries(classifiedByType)) {
      const color = TYPE_COLORS[type] || '#888';
      const label = TYPE_LABELS[type] || type;

      const points = data.measurements.map(m => ({ x: m.size, y: m.time }));

      datasets.push({
        label,
        data: points,
        borderColor: color,
        backgroundColor: color + '20',
        pointBackgroundColor: color,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2,
        tension: 0.3,
        fill: false,
      });

      // Theoretical fitted curve
      if (data.best && sizes.length > 1) {
        const curveSizes = generateCurveSizes(Math.min(...sizes), Math.max(...sizes), 40);
        const curveY = Classifier.theoreticalCurve(data.best.key, curveSizes, data.measurements);

        const curvePoints = curveSizes.map((s, i) => ({
          x: s,
          y: isFinite(curveY[i]) ? curveY[i] : null
        })).filter(p => p.y !== null);

        datasets.push({
          label: `${label} fit: ${data.best.label}`,
          data: curvePoints,
          borderColor: color,
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderDash: [5, 4],
          pointRadius: 0,
          tension: 0.4,
          fill: false,
        });
      }
    }

    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }

    const ctx = getCtx();
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: { datasets },
      options: buildOptions(),
    });
  }

  function buildOptions() {
    const isLog = currentScale === 'log';
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 400 },
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#7a899f',
            font: { family: "'JetBrains Mono', monospace", size: 11 },
            boxWidth: 14,
            padding: 12,
            usePointStyle: true,
          }
        },
        tooltip: {
          backgroundColor: '#161b26',
          borderColor: '#252d3d',
          borderWidth: 1,
          titleColor: '#e2e8f4',
          bodyColor: '#7a899f',
          titleFont: { family: "'JetBrains Mono', monospace", size: 12 },
          bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
          callbacks: {
            title: (items) => `n = ${items[0].parsed.x.toLocaleString()}`,
            label: (item) => {
              const v = item.parsed.y;
              return ` ${item.dataset.label}: ${formatTime(v)}`;
            }
          }
        }
      },
      scales: {
        x: {
          type: isLog ? 'logarithmic' : 'linear',
          title: {
            display: true,
            text: 'Input Size (n)',
            color: '#7a899f',
            font: { family: "'JetBrains Mono', monospace", size: 11 }
          },
          ticks: {
            color: '#4a5568',
            font: { family: "'JetBrains Mono', monospace", size: 10 },
            callback: (v) => v >= 1000 ? (v/1000).toFixed(v%1000===0?0:1)+'K' : v
          },
          grid: { color: '#1c2333' }
        },
        y: {
          type: isLog ? 'logarithmic' : 'linear',
          title: {
            display: true,
            text: 'Time (ms)',
            color: '#7a899f',
            font: { family: "'JetBrains Mono', monospace", size: 11 }
          },
          ticks: {
            color: '#4a5568',
            font: { family: "'JetBrains Mono', monospace", size: 10 },
            callback: (v) => formatTime(v)
          },
          grid: { color: '#1c2333' }
        }
      }
    };
  }

  function formatTime(ms) {
    if (ms === null || ms === undefined || !isFinite(ms)) return 'N/A';
    if (ms < 0.001) return '<0.001 ms';
    if (ms < 1) return ms.toFixed(3) + ' ms';
    if (ms < 1000) return ms.toFixed(2) + ' ms';
    return (ms / 1000).toFixed(2) + ' s';
  }

  function generateCurveSizes(min, max, count) {
    if (min === max) return [min];
    const result = [];
    for (let i = 0; i <= count; i++) {
      result.push(Math.round(min + (max - min) * (i / count)));
    }
    return [...new Set(result)].sort((a, b) => a - b);
  }

  function setScale(scale) {
    currentScale = scale;
    if (chartInstance && lastClassifiedData) {
      chartInstance.options = buildOptions();
      chartInstance.update('none');
    }
  }

  function exportPng() {
    if (!chartInstance) return;
    const link = document.createElement('a');
    link.download = 'algorithm-performance.png';
    link.href = chartInstance.toBase64Image('image/png', 1.0);
    link.click();
  }

  function clear() {
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
    const canvas = getCtx();
    if (canvas) canvas.style.display = 'none';
    const empty = document.getElementById('chart-empty');
    if (empty) empty.style.display = '';
    lastClassifiedData = null;
  }

  return { render, setScale, exportPng, clear, formatTime };
})();
