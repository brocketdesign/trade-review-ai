/**
 * Trade Review AI - Dashboard Application
 * 
 * Professional web application for visualizing trade analyses
 * with live market data support and manual trade entry
 */

// ===== Global State =====
let dashboardData = null;
let charts = {};
let symbolSearchTimeout = null;
let useLiveData = true;

// ===== Chart Configuration =====
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';
Chart.defaults.font.family = "'Inter', sans-serif";

const chartColors = {
    primary: '#6366f1',
    primaryLight: '#818cf8',
    success: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#0ea5e9',
    gray: '#64748b'
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize empty charts
    initializeCharts();
    
    // Load initial data
    runAnalysis();
    
    // Load manual trades
    loadManualTrades();
}

// ===== Event Listeners =====
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            navigateTo(section);
        });
    });
    
    // Run Analysis button
    document.getElementById('run-analysis').addEventListener('click', runAnalysis);
    
    // Close trade details
    document.getElementById('close-trade-details')?.addEventListener('click', () => {
        document.getElementById('trade-details-card').style.display = 'none';
    });
    
    // Data source selection
    document.getElementById('data-source').addEventListener('change', (e) => {
        useLiveData = e.target.value === 'live';
        const periodGroup = document.getElementById('period').parentElement;
        const intervalGroup = document.getElementById('interval').parentElement;
        const customDates = document.getElementById('custom-dates');
        
        if (useLiveData) {
            periodGroup.style.display = 'block';
            intervalGroup.style.display = 'block';
        } else {
            periodGroup.style.display = 'none';
            intervalGroup.style.display = 'none';
            customDates.style.display = 'block';
        }
    });
    
    // Period selection
    document.getElementById('period').addEventListener('change', (e) => {
        const customDates = document.getElementById('custom-dates');
        customDates.style.display = e.target.value === 'custom' ? 'block' : 'none';
    });
    
    // Symbol search with autocomplete
    const symbolInput = document.getElementById('symbol');
    symbolInput.addEventListener('input', (e) => {
        clearTimeout(symbolSearchTimeout);
        symbolSearchTimeout = setTimeout(() => searchSymbols(e.target.value), 300);
    });
    
    symbolInput.addEventListener('focus', () => {
        const suggestions = document.getElementById('symbol-suggestions');
        if (suggestions.children.length > 0) {
            suggestions.style.display = 'block';
        }
    });
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.symbol-input-wrapper')) {
            document.getElementById('symbol-suggestions').style.display = 'none';
        }
    });
    
    // Add trade form
    document.getElementById('add-trade-form')?.addEventListener('submit', handleAddTrade);
    document.getElementById('clear-form-btn')?.addEventListener('click', clearTradeForm);
    document.getElementById('clear-all-trades-btn')?.addEventListener('click', clearAllTrades);
}

// ===== Navigation =====
function navigateTo(section) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });
    
    // Update sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.toggle('active', sec.id === `${section}-section`);
    });
    
    // Update page title
    const titles = {
        dashboard: ['Dashboard', 'Overview of your trading performance'],
        trades: ['Trades', 'Detailed trade evaluations and analysis'],
        'add-trade': ['Add Trade', 'Enter manual trades for analysis'],
        analysis: ['AI Analysis', 'AI-generated insights and commentary'],
        market: ['Market Context', 'Market conditions and key levels']
    };
    
    const [title, subtitle] = titles[section] || ['Dashboard', ''];
    document.getElementById('page-title').textContent = title;
    document.getElementById('page-subtitle').textContent = subtitle;
}

// ===== Symbol Search =====
async function searchSymbols(query) {
    if (!query || query.length < 1) {
        document.getElementById('symbol-suggestions').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/live/search?q=${encodeURIComponent(query)}&limit=8`);
        const result = await response.json();
        
        if (result.success) {
            displaySymbolSuggestions(result.data);
        }
    } catch (error) {
        console.error('Symbol search error:', error);
    }
}

function displaySymbolSuggestions(suggestions) {
    const container = document.getElementById('symbol-suggestions');
    container.innerHTML = '';
    
    suggestions.forEach(item => {
        const div = document.createElement('div');
        div.className = 'symbol-suggestion-item';
        div.innerHTML = `
            <span class="symbol-ticker">${item.symbol}</span>
            <span class="symbol-name">${item.name}</span>
        `;
        div.addEventListener('click', () => {
            document.getElementById('symbol').value = item.symbol;
            container.style.display = 'none';
        });
        container.appendChild(div);
    });
    
    container.style.display = suggestions.length > 0 ? 'block' : 'none';
}

// ===== API Calls =====
async function runAnalysis() {
    const symbol = document.getElementById('symbol').value;
    const dataSource = document.getElementById('data-source').value;
    const period = document.getElementById('period').value;
    const interval = document.getElementById('interval').value;
    
    showLoading(true);
    updateStatus('Analyzing...');
    
    try {
        let url;
        if (dataSource === 'live') {
            // Use live data API
            if (period === 'custom') {
                const startDate = document.getElementById('start-date').value;
                const endDate = document.getElementById('end-date').value;
                url = `/api/live/analyze?symbol=${symbol}&start_date=${startDate}&end_date=${endDate}&interval=${interval}`;
            } else {
                url = `/api/live/analyze?symbol=${symbol}&period=${period}&interval=${interval}`;
            }
        } else {
            // Use sample data
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            url = `/api/dashboard-summary?symbol=${symbol}&start_date=${startDate}&end_date=${endDate}`;
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.success) {
            dashboardData = result.data;
            updateDashboard(dashboardData);
            showToast('Analysis completed successfully', 'success');
            updateStatus('Ready');
        } else {
            showToast(`Error: ${result.error}`, 'error');
            updateStatus('Error');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showToast('Failed to run analysis', 'error');
        updateStatus('Error');
    }
    
    showLoading(false);
}

// ===== Dashboard Updates =====
function updateDashboard(data) {
    const review = data.review;
    const marketData = data.market_data;
    
    // Update KPIs
    updateKPIs(review.overall_performance);
    
    // Update Charts
    updatePriceChart(marketData, review.trades);
    updatePerformanceChart(review.overall_performance);
    updateQualityCharts(review.evaluations);
    
    // Update Trades Table
    updateTradesTable(review.trades, review.evaluations);
    
    // Update AI Commentary
    updateAICommentary(review.ai_commentary);
    
    // Update Observations
    updateObservations(review.evaluations);
    
    // Update Market Context
    updateMarketContext(review.market_context);
    
    // Update Volume Chart
    updateVolumeChart(marketData);
    
    // Update trend badge
    updateTrendBadge(review.market_context.trend);
}

function updateKPIs(performance) {
    const totalPnl = performance.total_pnl;
    const pnlElement = document.getElementById('kpi-total-pnl');
    pnlElement.textContent = formatCurrency(totalPnl);
    pnlElement.className = `kpi-value ${totalPnl >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('kpi-win-rate').textContent = `${performance.win_rate.toFixed(1)}%`;
    document.getElementById('kpi-total-trades').textContent = performance.total_trades;
    
    const avgPnl = performance.avg_pnl;
    const avgPnlElement = document.getElementById('kpi-avg-pnl');
    avgPnlElement.textContent = formatCurrency(avgPnl);
    avgPnlElement.className = `kpi-value ${avgPnl >= 0 ? 'positive' : 'negative'}`;
}

function updateTrendBadge(trend) {
    const badge = document.getElementById('trend-badge');
    badge.textContent = trend.charAt(0).toUpperCase() + trend.slice(1);
    badge.className = `badge ${trend}`;
}

// ===== Charts =====
function initializeCharts() {
    // Price Chart
    const priceCtx = document.getElementById('price-chart').getContext('2d');
    charts.price = new Chart(priceCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                data: [],
                borderColor: chartColors.primary,
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    grid: { color: '#334155' },
                    ticks: {
                        callback: (value) => '$' + value.toFixed(2)
                    }
                }
            }
        }
    });
    
    // Performance Chart (Doughnut)
    const perfCtx = document.getElementById('performance-chart').getContext('2d');
    charts.performance = new Chart(perfCtx, {
        type: 'doughnut',
        data: {
            labels: ['Winning', 'Losing'],
            datasets: [{
                data: [0, 0],
                backgroundColor: [chartColors.success, chartColors.danger],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20 }
                }
            }
        }
    });
    
    // Entry Quality Chart
    const entryCtx = document.getElementById('entry-quality-chart').getContext('2d');
    charts.entryQuality = new Chart(entryCtx, {
        type: 'doughnut',
        data: {
            labels: ['Good', 'Acceptable', 'Poor'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [chartColors.success, chartColors.warning, chartColors.danger],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 15, boxWidth: 12 }
                }
            }
        }
    });
    
    // Discipline Chart
    const disciplineCtx = document.getElementById('discipline-chart').getContext('2d');
    charts.discipline = new Chart(disciplineCtx, {
        type: 'doughnut',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [chartColors.success, chartColors.warning, chartColors.danger],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 15, boxWidth: 12 }
                }
            }
        }
    });
    
    // Trend Alignment Chart
    const trendCtx = document.getElementById('trend-alignment-chart').getContext('2d');
    charts.trendAlignment = new Chart(trendCtx, {
        type: 'doughnut',
        data: {
            labels: ['With Trend', 'Against Trend'],
            datasets: [{
                data: [0, 0],
                backgroundColor: [chartColors.success, chartColors.danger],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 15, boxWidth: 12 }
                }
            }
        }
    });
    
    // Volume Chart
    const volumeCtx = document.getElementById('volume-chart').getContext('2d');
    charts.volume = new Chart(volumeCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Volume',
                data: [],
                backgroundColor: chartColors.info,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    grid: { color: '#334155' },
                    ticks: {
                        callback: (value) => formatNumber(value)
                    }
                }
            }
        }
    });
}

function updatePriceChart(marketData, trades) {
    const labels = marketData.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit' });
    });
    const prices = marketData.map(d => d.close);
    
    // Create trade markers
    const tradePoints = [];
    trades.forEach(trade => {
        const tradeTime = new Date(trade.timestamp).getTime();
        const dataIndex = marketData.findIndex(d => {
            const dataTime = new Date(d.timestamp).getTime();
            return Math.abs(dataTime - tradeTime) < 3600000; // Within 1 hour
        });
        
        if (dataIndex !== -1) {
            tradePoints.push({
                x: labels[dataIndex],
                y: trade.entry_price,
                trade: trade
            });
        }
    });
    
    charts.price.data.labels = labels;
    charts.price.data.datasets = [
        {
            label: 'Price',
            data: prices,
            borderColor: chartColors.primary,
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            fill: true,
            tension: 0.1,
            pointRadius: 0
        },
        {
            label: 'Trades',
            data: tradePoints,
            type: 'scatter',
            pointRadius: 8,
            pointBackgroundColor: tradePoints.map(p => 
                p.trade.side === 'buy' ? chartColors.success : chartColors.danger
            ),
            pointBorderColor: '#fff',
            pointBorderWidth: 2
        }
    ];
    charts.price.update();
}

function updatePerformanceChart(performance) {
    charts.performance.data.datasets[0].data = [
        performance.winning_trades,
        performance.losing_trades
    ];
    charts.performance.update();
}

function updateQualityCharts(evaluations) {
    // Entry Quality
    const entryQuality = { good: 0, acceptable: 0, poor: 0 };
    evaluations.forEach(e => entryQuality[e.entry_quality]++);
    charts.entryQuality.data.datasets[0].data = [
        entryQuality.good,
        entryQuality.acceptable,
        entryQuality.poor
    ];
    charts.entryQuality.update();
    
    // Discipline
    const discipline = { high: 0, medium: 0, low: 0 };
    evaluations.forEach(e => discipline[e.execution_discipline]++);
    charts.discipline.data.datasets[0].data = [
        discipline.high,
        discipline.medium,
        discipline.low
    ];
    charts.discipline.update();
    
    // Trend Alignment
    const withTrend = evaluations.filter(e => e.aligned_with_trend).length;
    const againstTrend = evaluations.length - withTrend;
    charts.trendAlignment.data.datasets[0].data = [withTrend, againstTrend];
    charts.trendAlignment.update();
}

function updateVolumeChart(marketData) {
    const labels = marketData.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit' });
    });
    const volumes = marketData.map(d => d.volume);
    
    charts.volume.data.labels = labels;
    charts.volume.data.datasets[0].data = volumes;
    charts.volume.update();
}

// ===== Trades Table =====
function updateTradesTable(trades, evaluations) {
    const tbody = document.getElementById('trades-table-body');
    tbody.innerHTML = '';
    
    trades.forEach((trade, index) => {
        const evaluation = evaluations[index];
        const row = document.createElement('tr');
        row.addEventListener('click', () => showTradeDetails(trade, evaluation));
        
        const status = trade.exit_price ? 'CLOSED' : 'OPEN';
        const pnl = trade.pnl;
        
        row.innerHTML = `
            <td><strong>${trade.trade_id}</strong></td>
            <td><span class="trade-side ${trade.side}">${trade.side.toUpperCase()}</span></td>
            <td>$${trade.entry_price.toFixed(2)}</td>
            <td>${trade.exit_price ? '$' + trade.exit_price.toFixed(2) : '-'}</td>
            <td><span class="pnl-value ${pnl > 0 ? 'positive' : pnl < 0 ? 'negative' : ''}">${pnl !== null ? formatCurrency(pnl) : '-'}</span></td>
            <td><span class="quality-badge ${evaluation.entry_quality}">${evaluation.entry_quality}</span></td>
            <td><span class="quality-badge ${evaluation.execution_discipline}">${evaluation.execution_discipline}</span></td>
            <td>${evaluation.aligned_with_trend ? '✓ Yes' : '✗ No'}</td>
            <td><span class="status-badge ${status.toLowerCase()}">${status}</span></td>
        `;
        
        tbody.appendChild(row);
    });
    
    document.getElementById('trades-count').textContent = `${trades.length} trades`;
}

function showTradeDetails(trade, evaluation) {
    const card = document.getElementById('trade-details-card');
    const content = document.getElementById('trade-details-content');
    
    content.innerHTML = `
        <div class="trade-detail-grid">
            <div class="detail-item">
                <span class="detail-label">Trade ID</span>
                <span class="detail-value">${trade.trade_id}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Symbol</span>
                <span class="detail-value">${trade.symbol}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Side</span>
                <span class="detail-value"><span class="trade-side ${trade.side}">${trade.side.toUpperCase()}</span></span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Entry Price</span>
                <span class="detail-value">$${trade.entry_price.toFixed(2)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Exit Price</span>
                <span class="detail-value">${trade.exit_price ? '$' + trade.exit_price.toFixed(2) : '-'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Quantity</span>
                <span class="detail-value">${trade.quantity}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Stop Loss</span>
                <span class="detail-value">${trade.stop_loss ? '$' + trade.stop_loss.toFixed(2) : '-'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Take Profit</span>
                <span class="detail-value">${trade.take_profit ? '$' + trade.take_profit.toFixed(2) : '-'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">P&L</span>
                <span class="detail-value ${trade.pnl > 0 ? 'positive' : trade.pnl < 0 ? 'negative' : ''}">${trade.pnl !== null ? formatCurrency(trade.pnl) : '-'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Entry Quality</span>
                <span class="detail-value"><span class="quality-badge ${evaluation.entry_quality}">${evaluation.entry_quality}</span></span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Exit Quality</span>
                <span class="detail-value"><span class="quality-badge ${evaluation.exit_quality || 'n-a'}">${evaluation.exit_quality || 'N/A'}</span></span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Risk/Reward</span>
                <span class="detail-value">${evaluation.risk_reward_ratio ? evaluation.risk_reward_ratio.toFixed(2) : '-'}</span>
            </div>
        </div>
        ${trade.notes ? `
        <div class="observations-section">
            <h4>Trade Notes</h4>
            <div class="observation-item">
                <i data-lucide="file-text"></i>
                <span>${trade.notes}</span>
            </div>
        </div>
        ` : ''}
        ${evaluation.key_observations && evaluation.key_observations.length > 0 ? `
        <div class="observations-section">
            <h4>Key Observations</h4>
            ${evaluation.key_observations.map(obs => `
                <div class="observation-item">
                    <i data-lucide="lightbulb"></i>
                    <span>${obs}</span>
                </div>
            `).join('')}
        </div>
        ` : ''}
    `;
    
    card.style.display = 'block';
    lucide.createIcons();
}

// ===== AI Commentary =====
function updateAICommentary(commentary) {
    const container = document.getElementById('ai-commentary');
    container.innerHTML = `<div class="commentary-text">${formatCommentary(commentary)}</div>`;
}

function formatCommentary(text) {
    // Convert markdown-like formatting to HTML
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
}

function updateObservations(evaluations) {
    const container = document.getElementById('observations-list');
    container.innerHTML = '';
    
    evaluations.forEach(evaluation => {
        if (evaluation.key_observations && evaluation.key_observations.length > 0) {
            const tradeDiv = document.createElement('div');
            tradeDiv.className = 'observation-trade';
            
            tradeDiv.innerHTML = `
                <div class="observation-trade-header">
                    <i data-lucide="bar-chart-2"></i>
                    Trade ${evaluation.trade_id}
                </div>
                ${evaluation.key_observations.map(obs => `
                    <div class="observation-item">
                        <i data-lucide="lightbulb"></i>
                        <span>${obs}</span>
                    </div>
                `).join('')}
            `;
            
            container.appendChild(tradeDiv);
        }
    });
    
    lucide.createIcons();
}

// ===== Market Context =====
function updateMarketContext(context) {
    document.getElementById('market-symbol').textContent = context.symbol;
    document.getElementById('market-trend').textContent = 
        context.trend.charAt(0).toUpperCase() + context.trend.slice(1);
    document.getElementById('market-trend-strength').textContent = 
        (context.trend_strength * 100).toFixed(1) + '%';
    document.getElementById('market-volatility').textContent = 
        '$' + context.volatility.toFixed(2);
    document.getElementById('market-volume').textContent = 
        formatNumber(context.average_volume);
    
    // Support Levels
    const supportList = document.getElementById('support-levels');
    supportList.innerHTML = context.support_levels
        .map(level => `<li>$${level.toFixed(2)}</li>`)
        .join('');
    
    // Resistance Levels
    const resistanceList = document.getElementById('resistance-levels');
    resistanceList.innerHTML = context.resistance_levels
        .map(level => `<li>$${level.toFixed(2)}</li>`)
        .join('');
}

// ===== UI Helpers =====
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.toggle('active', show);
}

function updateStatus(status) {
    const indicator = document.getElementById('status-indicator');
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('.status-text');
    
    text.textContent = status;
    
    if (status === 'Error') {
        dot.style.background = '#ef4444';
    } else if (status === 'Analyzing...') {
        dot.style.background = '#f59e0b';
    } else {
        dot.style.background = '#10b981';
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 'alert-circle';
    toast.innerHTML = `
        <i data-lucide="${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ===== Formatting Helpers =====
function formatCurrency(value) {
    const absValue = Math.abs(value);
    const formatted = absValue.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return value < 0 ? `-${formatted}` : formatted;
}

function formatNumber(value) {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K';
    }
    return value.toString();
}

// ===== Manual Trade Management =====
async function handleAddTrade(e) {
    e.preventDefault();
    
    const symbol = document.getElementById('trade-symbol').value.toUpperCase();
    const side = document.getElementById('trade-side').value;
    const entryPrice = parseFloat(document.getElementById('trade-entry-price').value);
    const quantity = parseFloat(document.getElementById('trade-quantity').value);
    const entryTime = document.getElementById('trade-entry-time').value;
    const exitPrice = document.getElementById('trade-exit-price').value;
    const stopLoss = document.getElementById('trade-stop-loss').value;
    const takeProfit = document.getElementById('trade-take-profit').value;
    const notes = document.getElementById('trade-notes').value;
    
    const tradeData = {
        symbol,
        side,
        entry_price: entryPrice,
        quantity,
        timestamp: entryTime || null,
        exit_price: exitPrice ? parseFloat(exitPrice) : null,
        stop_loss: stopLoss ? parseFloat(stopLoss) : null,
        take_profit: takeProfit ? parseFloat(takeProfit) : null,
        notes: notes || null
    };
    
    try {
        const response = await fetch('/api/trades/manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tradeData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`Trade ${result.data.trade_id} added successfully`, 'success');
            clearTradeForm();
            loadManualTrades();
            
            // Auto-fill the analysis symbol
            document.getElementById('symbol').value = symbol;
        } else {
            showToast(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Add trade error:', error);
        showToast('Failed to add trade', 'error');
    }
}

function clearTradeForm() {
    document.getElementById('add-trade-form').reset();
    // Set default values
    document.getElementById('trade-side').value = 'buy';
}

async function loadManualTrades() {
    try {
        const response = await fetch('/api/trades/manual');
        const result = await response.json();
        
        if (result.success) {
            updateManualTradesTable(result.data);
        }
    } catch (error) {
        console.error('Load trades error:', error);
    }
}

function updateManualTradesTable(trades) {
    const tbody = document.getElementById('manual-trades-table-body');
    if (!tbody) return;
    
    if (trades.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="9">No manual trades yet. Add your first trade above.</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = '';
    
    trades.forEach(trade => {
        const row = document.createElement('tr');
        const status = trade.exit_price ? 'CLOSED' : 'OPEN';
        const pnl = trade.pnl;
        
        row.innerHTML = `
            <td><strong>${trade.trade_id}</strong></td>
            <td>${trade.symbol}</td>
            <td><span class="trade-side ${trade.side}">${trade.side.toUpperCase()}</span></td>
            <td>$${trade.entry_price.toFixed(2)}</td>
            <td>${trade.exit_price ? '$' + trade.exit_price.toFixed(2) : '-'}</td>
            <td>${trade.quantity}</td>
            <td><span class="pnl-value ${pnl > 0 ? 'positive' : pnl < 0 ? 'negative' : ''}">${pnl !== null ? formatCurrency(pnl) : '-'}</span></td>
            <td><span class="status-badge ${status.toLowerCase()}">${status}</span></td>
            <td>
                <button class="btn-icon delete-trade-btn" data-trade-id="${trade.trade_id}" title="Delete trade">
                    <i data-lucide="trash-2"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Re-initialize icons
    lucide.createIcons();
    
    // Add delete handlers
    document.querySelectorAll('.delete-trade-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const tradeId = btn.dataset.tradeId;
            deleteTrade(tradeId);
        });
    });
}

async function deleteTrade(tradeId) {
    if (!confirm(`Are you sure you want to delete trade ${tradeId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/trades/manual/${tradeId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`Trade ${tradeId} deleted`, 'success');
            loadManualTrades();
        } else {
            showToast(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Delete trade error:', error);
        showToast('Failed to delete trade', 'error');
    }
}

async function clearAllTrades() {
    if (!confirm('Are you sure you want to delete ALL manual trades? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/trades/manual/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('All trades cleared', 'success');
            loadManualTrades();
        } else {
            showToast(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Clear trades error:', error);
        showToast('Failed to clear trades', 'error');
    }
}
