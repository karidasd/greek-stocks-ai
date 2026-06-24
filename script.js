let currentData = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    setupFilters();
});

async function fetchData() {
    try {
        const timestamp = new Date().getTime();
        const response = await fetch(`data/stocks.json?t=${timestamp}`);
        if (!response.ok) throw new Error('Data file not found');
        
        currentData = await response.json();
        
        document.getElementById('last-update').textContent = `Last Update: ${currentData.date}`;
        
        renderFearGreed(currentData.fear_greed);
        renderSOTD(currentData);
        renderStocksGrid(currentData.stocks);
        
    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('stocks-grid').innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--neon-red);">
                <h3>Σφάλμα Φόρτωσης Δεδομένων</h3>
                <p>Παρακαλώ περιμένετε το επόμενο update.</p>
            </div>
        `;
    }
}

function renderNews(newsArray) {
    const marquee = document.getElementById('news-marquee');
    if (!marquee || !newsArray || newsArray.length === 0) return;
    
    let html = '<div class="news-content">';
    newsArray.forEach(n => {
        html += `<a href="${n.link}" target="_blank">📰 ${n.title}</a>`;
    });
    // Duplicate for smooth infinite scroll
    newsArray.forEach(n => {
        html += `<a href="${n.link}" target="_blank">📰 ${n.title}</a>`;
    });
    html += '</div>';
    marquee.innerHTML = html;
}

function renderFearGreed(fg) {
    if (!fg) return;
    document.getElementById('fear-greed-section').style.display = 'block';
    
    const scoreElem = document.getElementById('fg-score');
    const labelElem = document.getElementById('fg-label');
    const markerElem = document.getElementById('fg-marker');
    
    scoreElem.textContent = fg.score;
    labelElem.textContent = fg.status;
    
    // Position marker (0 to 100%)
    markerElem.style.left = `calc(${fg.score}% - 2px)`;
    
    // Colorize based on score
    if (fg.score > 55) {
        scoreElem.style.color = 'var(--neon-green)';
        labelElem.style.background = 'rgba(16, 185, 129, 0.2)';
        labelElem.style.color = 'var(--neon-green)';
    } else if (fg.score < 45) {
        scoreElem.style.color = 'var(--neon-red)';
        labelElem.style.background = 'rgba(239, 68, 68, 0.2)';
        labelElem.style.color = 'var(--neon-red)';
    } else {
        scoreElem.style.color = 'var(--neon-yellow)';
        labelElem.style.background = 'rgba(245, 158, 11, 0.2)';
        labelElem.style.color = 'var(--neon-yellow)';
    }
}

function setupFilters() {
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!currentData) return;
            
            buttons.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const sortType = e.target.getAttribute('data-sort');
            let sortedStocks = [...currentData.stocks];
            
            if (sortType === 'gainers') {
                sortedStocks.sort((a, b) => b.change_pct - a.change_pct);
            } else if (sortType === 'losers') {
                sortedStocks.sort((a, b) => a.change_pct - b.change_pct);
            } else if (sortType === 'ai') {
                const score = s => (s.tech_tip.includes('BUY') ? 2 : (s.tech_tip.includes('SELL') ? -2 : 0)) + (s.sentiment.includes('Bullish') ? 1 : (s.sentiment.includes('Bearish') ? -1 : 0));
                sortedStocks.sort((a, b) => score(b) - score(a));
            } else {
                sortedStocks.sort((a, b) => a.name.localeCompare(b.name));
            }
            
            renderStocksGrid(sortedStocks);
        });
    });
}

function getBadgeClass(tip) {
    const t = tip.toLowerCase();
    if (t.includes('strong buy')) return 'badge strong-buy';
    if (t.includes('buy')) return 'badge buy';
    if (t.includes('strong sell')) return 'badge strong-sell';
    if (t.includes('sell')) return 'badge sell';
    return 'badge hold';
}

function getSentimentBadgeClass(sent) {
    const s = sent.toLowerCase();
    if (s === 'bullish') return 'badge bullish';
    if (s === 'bearish') return 'badge bearish';
    return 'badge neutral';
}

function getPatternBadge(pattern) {
    if (pattern === 'Golden Cross') return '<span class="badge pattern">🌟 Golden Cross</span>';
    if (pattern === 'Death Cross') return '<span class="badge pattern death">💀 Death Cross</span>';
    return '';
}

function generateSparkline(prices, isUp) {
    if (!prices || prices.length < 2) return '';
    
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;
    
    const width = 100;
    const height = 30;
    
    const points = prices.map((price, i) => {
        const x = (i / (prices.length - 1)) * width;
        const y = height - ((price - min) / range) * height;
        return `${x},${y}`;
    }).join(' ');
    
    const color = isUp ? 'var(--neon-green)' : 'var(--neon-red)';
    
    return `
        <svg viewBox="-2 -2 104 34" width="100%" height="40" preserveAspectRatio="none">
            <polyline fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="${points}" />
        </svg>
    `;
}

function renderSOTD(data) {
    if (!data.sotd) return;
    
    const stock = data.stocks.find(s => s.ticker === data.sotd);
    if (!stock) return;
    
    const isUp = stock.change_pct >= 0;
    const changeClass = isUp ? 'up' : 'down';
    const changeSign = isUp ? '+' : '';
    
    const sparklineHTML = generateSparkline(stock.sparkline, isUp);
    
    const html = `
        <div class="sotd-main">
            <span class="sotd-ticker">${stock.ticker.replace('.AT', '')}</span>
            <span class="sotd-name">${stock.name}</span>
            <div class="sotd-price-container">
                <span class="sotd-price">€${stock.price.toFixed(3)}</span>
                <span class="sotd-change ${changeClass}" style="background: ${isUp ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)'}">
                    ${changeSign}${stock.change_pct}%
                </span>
            </div>
            <div class="sparkline-container" style="width: 150px; margin-top: 10px;">
                ${sparklineHTML}
            </div>
        </div>
        <div class="fundamentals">
            <div class="fund-box">
                <span class="fund-label">P/E Ratio</span>
                <span class="fund-value">${stock.pe_ratio}</span>
            </div>
            <div class="fund-box" style="align-items: flex-end;">
                <span class="fund-label">Dividend Yield</span>
                <span class="fund-value ${stock.dividend_yield > 0 ? 'badge gold' : ''}" style="padding: 2px 6px;">${stock.dividend_yield > 0 ? stock.dividend_yield + '%' : '-'}</span>
            </div>
        </div>
        <div class="sotd-badges">
            ${stock.volume_breakout ? '<span class="badge volume">🔥 High Volume</span>' : ''}
            <div class="stat-box" style="align-items: flex-end;">
                <span class="stat-label">AI Signal</span>
                <span class="stat-value" style="color: var(--accent);">${stock.tech_tip}</span>
            </div>
            ${data.sotd_win_rate ? `
            <div class="stat-box" style="align-items: flex-end; margin-left: 10px;">
                <span class="stat-label">AI Win Rate</span>
                <span class="stat-value" style="color: var(--success);">${data.sotd_win_rate.rate}% <span style="font-size:0.6rem;color:var(--text-secondary)">(${data.sotd_win_rate.total}d)</span></span>
            </div>` : ''}
        </div>
    `;
    
    document.getElementById('sotd-card').innerHTML = html;
    document.getElementById('sotd-container').style.display = 'block';
}

function renderStocksGrid(stocks) {
    const grid = document.getElementById('stocks-grid');
    grid.innerHTML = '';
    
    stocks.forEach(stock => {
        const isUp = stock.change_pct >= 0;
        const changeClass = isUp ? 'up' : 'down';
        const changeSign = isUp ? '+' : '';
        
        const card = document.createElement('div');
        card.className = 'stock-card';
        if (stock.is_sotd) {
            card.style.borderColor = 'var(--accent-blue)';
            card.style.boxShadow = '0 0 15px rgba(59,130,246,0.2)';
        }
        
        const sparklineHTML = generateSparkline(stock.sparkline, isUp);
        const patternBadge = getPatternBadge(stock.pattern);
        
        card.innerHTML = `
            ${patternBadge}
            ${stock.volume_breakout ? '<span class="badge volume">🔥 High Volume</span>' : ''}
            <div class="stock-header">
                <div class="stock-info">
                    <h3>${stock.name}</h3>
                    <span>${stock.ticker.replace('.AT', '')}</span>
                </div>
                <div class="stock-price-info">
                    <span class="price">€${stock.price.toFixed(3)}</span>
                    <span class="change ${changeClass}">${changeSign}${stock.change_pct}%</span>
                </div>
            </div>
            
            <div class="sparkline-container">
                ${sparklineHTML}
            </div>
            
            <div class="fundamentals">
                <div class="fund-box">
                    <span class="fund-label">P/E Ratio</span>
                    <span class="fund-value">${stock.pe_ratio}</span>
                </div>
                <div class="fund-box" style="align-items: flex-end;">
                    <span class="fund-label">Dividend</span>
                    <span class="fund-value ${stock.dividend_yield > 0 ? 'badge gold' : ''}" style="padding: 2px 6px;">${stock.dividend_yield > 0 ? stock.dividend_yield + '%' : '-'}</span>
                </div>
            </div>
            
            <div class="stock-stats">
                <div class="stat-box">
                    <span class="stat-label">Tech Signal</span>
                    <span class="${getBadgeClass(stock.tech_tip)}">${stock.tech_tip}</span>
                </div>
                <div class="stat-box" style="align-items: flex-end;">
                    <span class="stat-label">Sentiment</span>
                    <span class="${getSentimentBadgeClass(stock.sentiment)}">${stock.sentiment}</span>
                </div>
            </div>
            ${stock.upcoming_event ? `<div class="event-badge">🔔 ${stock.upcoming_event}</div>` : ''}
        `;
        
        grid.appendChild(card);
    });
}
