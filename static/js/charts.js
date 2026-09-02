/**
 * Chart.js Visualizations for Communication Growth Dashboard
 */
let componentRadarChart = null;
let historicalTrendChart = null;

function initComponentRadarChart(componentScores) {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;

  const labels = Object.keys(componentScores);
  const dataValues = Object.values(componentScores);

  if (componentRadarChart) {
    componentRadarChart.destroy();
  }

  componentRadarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Current Skill Proficiency',
        data: dataValues,
        backgroundColor: 'rgba(99, 102, 241, 0.25)',
        borderColor: '#6366f1',
        borderWidth: 2,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#8b5cf6'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          pointLabels: {
            color: '#94a3b8',
            font: { size: 12, family: 'Outfit', weight: '600' }
          },
          ticks: {
            color: '#64748b',
            backdropColor: 'transparent',
            suggestedMin: 30,
            suggestedMax: 100
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function initHistoricalTrendChart(recentTrend) {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;

  const labels = recentTrend.map(t => t.session);
  const scores = recentTrend.map(t => t.score);
  const wpms = recentTrend.map(t => t.wpm);

  if (historicalTrendChart) {
    historicalTrendChart.destroy();
  }

  historicalTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Overall Score',
          data: scores,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          tension: 0.4,
          fill: true,
          yAxisID: 'y'
        },
        {
          label: 'WPM',
          data: wpms,
          borderColor: '#06b6d4',
          borderDash: [5, 5],
          tension: 0.4,
          fill: false,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8' }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8' },
          min: 40,
          max: 100
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#06b6d4' },
          min: 80,
          max: 200
        }
      },
      plugins: {
        legend: {
          labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans' } }
        }
      }
    }
  });
}
