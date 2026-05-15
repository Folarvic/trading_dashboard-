// AI Trading Dashboard - Frontend Logic
// Auto-refreshes every 15 minutes (900000 ms)

const API_BASE_URL = 'http://localhost:8000/api';
const UPDATE_INTERVAL = 900000; // 15 minutes
let charts = {};
let lastData = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 AI Trading Dashboard initializing...');

    // Initial load
    refreshData();

    // Auto-refresh every 15 minutes
    setInterval(refreshData, UPDATE_INTERVAL);

    // Countdown timer for next update
    startCountdown();
});

// Fetch and update all data
async function refreshData() {
    try {
        showLoading();

        const response = await fetch(`${API_BASE_URL}/portfolio/latest`);
        if (!response.ok) throw new Error('API Error');

        const data = await response.json();
        lastData = data;

        updateDashboard(data);
        updateLastUpdateTime();

        console.log('✅ Dashboard updated:', new Date().toLocaleTimeString());
    } catch (error) {
        console.error('❌ Error fetching data:', error);
        showError('Failed to fetch data. Retrying in 60s...');

        // Retry in 60 seconds
        setTimeout(refreshData, 60000);
    }
}

// Update all dashboard components
function updateDashboard(data) {
    updatePortfolioCards(data);
    updatePositionsTable(data);
    updateRiskMetrics(data);
    updateCharts(data);
}

// Update portfolio summary cards
function updatePortfolioCards(data) {
    const portfolioValue = data.portfolio_value || 100000;
    const positions = data.positions || {};

    // Calculate P&L
    let totalPnl = 0;
    let activeCount = 0;

    for (const [asset, pos] of Object.entries(positions)) {
        if (pos && pos.signal && Math.abs(pos.signal) > 0.2) {
            activeCount++;
        }
    }

    document.getElementById('portfolio-value').textContent = 
        '$' + portfolioValue.toLocaleString('en-US', {minimumFractionDigits: 2});

    document.getElementById('daily-pnl').textContent = 
        (totalPnl >= 0 ? '+' : '') + '$' + totalPnl.toFixed(2);
    document.getElementById('daily-pnl').className = 'card-value ' + (totalPnl >= 0 ? 'positive' : 'negative');

    document.getElementById('pnl-change').textContent = 
        (totalPnl / portfolioValue * 100).toFixed(2) + '%';
    document.getElementById('pnl-change').className = 'card-change ' + 
        (totalPnl >= 0 ? 'positive' : 'negative');

    document.getElementById('active-positions').textContent = 
        activeCount + '/7';
}

// Update positions table
function updatePositionsTable(data) {
    const tbody = document.getElementById('positions-body');
    const positions = data.positions || {};
    const signals = data.signals || {};

    tbody.innerHTML = '';

    for (const [asset, pos] of Object.entries(positions)) {
        const signal = signals[asset];
        if (!signal) continue;

        const row = document.createElement('tr');

        // Signal badge
        let badgeClass = 'signal-hold';
        let badgeText = 'HOLD';
        if (signal.ensemble > 0.5) { badgeClass = 'signal-strong-buy'; badgeText = 'STRONG BUY'; }
        else if (signal.ensemble > 0.2) { badgeClass = 'signal-buy'; badgeText = 'BUY'; }
        else if (signal.ensemble < -0.5) { badgeClass = 'signal-strong-sell'; badgeText = 'STRONG SELL'; }
        else if (signal.ensemble < -0.2) { badgeClass = 'signal-sell'; badgeText = 'SELL'; }

        // P&L (placeholder - would calculate from entry)
        const pnl = 0; // Calculate from stored entry vs current price

        row.innerHTML = `
            <td><strong>${asset}</strong></td>
            <td>${pos.price?.toFixed(4) || '-'}</td>
            <td><span class="signal-badge ${badgeClass}">${badgeText}</span></td>
            <td>${(pos.weight * 100).toFixed(2)}%</td>
            <td>${pos.stop?.toFixed(4) || '-'}</td>
            <td>${pos.target?.toFixed(4) || '-'}</td>
            <td class="${pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">
                ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}
            </td>
            <td>${pos.direction || '-'}</td>
        `;

        tbody.appendChild(row);
    }

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr class="loading-row"><td colspan="8">No active positions</td></tr>';
    }
}

// Update risk metrics
function updateRiskMetrics(data) {
    const risk = data.portfolio_risk || {};
    const riskPct = risk.total_risk_pct || 0;

    document.getElementById('portfolio-risk').textContent = riskPct.toFixed(2) + '%';

    const fill = document.getElementById('risk-fill');
    fill.style.width = Math.min(riskPct / 2 * 100, 100) + '%';

    if (riskPct > 1.5) {
        fill.className = 'risk-fill danger';
    } else if (riskPct > 1.0) {
        fill.className = 'risk-fill warning';
    } else {
        fill.className = 'risk-fill';
    }
}

// Update charts
function updateCharts(data) {
    updateSignalsChart(data.signals);
    updatePnlChart(data);
}

// Signal strength chart
function updateSignalsChart(signals) {
    const ctx = document.getElementById('signals-chart');
    if (!ctx) return;

    const labels = Object.keys(signals);
    const values = labels.map(a => signals[a]?.ensemble || 0);
    const colors = values.map(v => 
        v > 0.2 ? 'rgba(0,255,127,0.8)' : 
        v < -0.2 ? 'rgba(255,68,68,0.8)' : 
        'rgba(136,136,136,0.8)'
    );

    if (charts.signals) {
        charts.signals.destroy();
    }

    charts.signals = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ensemble Signal',
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Signal: ${ctx.raw.toFixed(3)}`
                    }
                }
            },
            scales: {
                y: {
                    min: -1,
                    max: 1,
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    ticks: { color: '#a0a0b0', font: { family: 'JetBrains Mono' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a0b0', font: { family: 'JetBrains Mono' } }
                }
            }
        }
    });
}

// P&L evolution chart (placeholder - would use historical data)
function updatePnlChart(data) {
    const ctx = document.getElementById('pnl-chart');
    if (!ctx) return;

    // Mock historical data - replace with actual API call to /api/history
    const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
    const pnlData = hours.map(() => (Math.random() - 0.5) * 200);

    if (charts.pnl) {
        charts.pnl.destroy();
    }

    charts.pnl = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [{
                label: 'Portfolio P&L ($)',
                data: pnlData,
                borderColor: '#4ECDC4',
                backgroundColor: 'rgba(78,205,196,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    ticks: { color: '#a0a0b0', font: { family: 'JetBrains Mono' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a0b0', font: { family: 'JetBrains Mono' } }
                }
            }
        }
    });
}

// Update last update time
function updateLastUpdateTime() {
    const now = new Date();
    document.getElementById('last-update').textContent = 
        'Updated: ' + now.toLocaleTimeString();
}

// Countdown timer for next update
function startCountdown() {
    const nextUpdateEl = document.getElementById('next-update');
    let seconds = 900; // 15 minutes

    setInterval(() => {
        seconds--;
        if (seconds <= 0) seconds = 900;

        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        nextUpdateEl.textContent = `Next: ${mins}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
}

// Show loading state
function showLoading() {
    const tbody = document.getElementById('positions-body');
    tbody.innerHTML = '<tr class="loading-row"><td colspan="8">Loading data...</td></tr>';
}

// Show error message
function showError(message) {
    const tbody = document.getElementById('positions-body');
    tbody.innerHTML = `<tr class="loading-row"><td colspan="8" style="color:#FF4444">${message}</td></tr>`;
}

// Manual refresh button handler
function manualRefresh() {
    console.log('🔄 Manual refresh triggered');
    refreshData();
}

// WebSocket connection (for real-time updates)
function connectWebSocket() {
    const socket = io('ws://localhost:8000');

    socket.on('connect', () => {
        console.log('🔌 WebSocket connected');
        document.getElementById('connection-status').textContent = 'Live';
    });

    socket.on('portfolio_update', (data) => {
        console.log('📡 Real-time update received');
        updateDashboard(data);
    });

    socket.on('disconnect', () => {
        console.log('🔌 WebSocket disconnected');
        document.getElementById('connection-status').textContent = 'Reconnecting...';
    });
}

// Export for global access
window.refreshData = refreshData;
window.manualRefresh = manualRefresh;
