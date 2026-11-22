/**
 * Academic Evaluation Charts for JobShield (Chart.js)
 */

let featureChartInstance = null;

function renderFeatureChart(topFraudTokens, topLegitTokens) {
  const canvas = document.getElementById('featureChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Select top 8 fraud and top 8 legit tokens
  const fraudItems = (topFraudTokens || []).slice(0, 8);
  const legitItems = (topLegitTokens || []).slice(0, 8);

  const labels = [
    ...fraudItems.map(item => `⚠️ ${item.token}`),
    ...legitItems.map(item => `✅ ${item.token}`)
  ];

  const dataValues = [
    ...fraudItems.map(item => item.weight),
    ...legitItems.map(item => -Math.abs(item.weight))
  ];

  const backgroundColors = [
    ...fraudItems.map(() => 'rgba(244, 63, 94, 0.75)'),
    ...legitItems.map(() => 'rgba(16, 185, 129, 0.75)')
  ];

  if (featureChartInstance) {
    featureChartInstance.destroy();
  }

  featureChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Attribution Coefficient (NLP TF-IDF Weight)',
        data: dataValues,
        backgroundColor: backgroundColors,
        borderRadius: 6,
        borderWidth: 0
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.raw;
              return val > 0 
                ? `Deceptive Fraud Indicator: +${val.toFixed(2)}`
                : `Legitimate Indicator: ${val.toFixed(2)}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(51, 65, 85, 0.3)' },
          ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#e2e8f0', font: { family: 'Plus Jakarta Sans', size: 11 } }
        }
      }
    }
  });
}
