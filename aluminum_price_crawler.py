<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>电解铝实时价格</title>
    <link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #1a73e8;
            --success: #34a853;
            --danger: #ea4335;
            --text: #333;
            --bg: #f8f9fa;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .price-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 500px;
            overflow: hidden;
        }
        .card-header {
            background: var(--primary);
            color: white;
            padding: 24px;
            text-align: center;
            position: relative;
        }
        .card-header h1 {
            font-size: 22px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        .price-section {
            padding: 30px 20px;
            text-align: center;
        }
        .price-value {
            font-size: 48px;
            font-weight: 700;
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .price-unit {
            font-size: 24px;
            margin-left: 8px;
            font-weight: 500;
        }
        .price-time {
            color: #666;
            font-size: 14px;
            margin: 8px 0;
        }
        .refresh-btn {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 500;
            margin: 15px 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 80%;
            max-width: 200px;
            margin: 20px auto;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(26, 115, 232, 0.25);
        }
        .refresh-btn:hover {
            background: #1669d8;
            transform: translateY(-2px);
        }
        .trend-chart {
            background: var(--bg);
            border-radius: 12px;
            padding: 15px;
            margin: 0 20px 30px;
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .chart-title {
            font-size: 16px;
            font-weight: 600;
        }
        .chart-range {
            color: var(--primary);
            font-size: 14px;
        }
        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
            font-size: 14px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .chart-container {
            height: 180px;
            position: relative;
        }
        .chart-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #999;
        }
        .footer {
            text-align: center;
            padding: 15px;
            font-size: 12px;
            color: #777;
            border-top: 1px solid #eee;
        }
        .loading {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10;
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(26, 115, 232, 0.2);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* 趋势动画 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
            animation: fadeIn 0.5s ease forwards;
        }
        
        /* 价格变动样式 */
        .price-up {
            color: var(--danger);
        }
        .price-up::after {
            content: "▲";
            font-size: 20px;
            margin-left: 8px;
        }
        .price-down {
            color: var(--success);
        }
        .price-down::after {
            content: "▼";
            font-size: 20px;
            margin-left: 8px;
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="price-card">
        <div class="card-header">
            <h1>电解铝实时价格</h1>
        </div>
        
        <div class="price-section">
            <div class="price-value animate-fadeIn" id="current-price">
                <span class="loading-text">--</span><span class="price-unit">元/吨</span>
            </div>
            <div class="price-time">
                更新时间：<span id="update-time">--</span>
            </div>
            
            <button class="refresh-btn" id="refresh-btn">
                <i class="fas fa-sync-alt"></i> 刷新数据
            </button>
        </div>
        
        <div class="trend-chart">
            <div class="chart-header">
                <div class="chart-title">近7天价格走势</div>
                <div class="chart-range">每日更新</div>
            </div>
            <div class="chart-container">
                <div class="chart-placeholder" id="chart-placeholder">
                    <div>加载趋势图...</div>
                </div>
                <!-- 趋势图占位符 -->
                <canvas id="trend-chart" width="400" height="180"></canvas>
            </div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #1a73e8;"></div>
                    <span>当日价格</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            数据来源：上海有色网 (SMM) 每日电解铝A00报价
        </div>
    </div>

    <div class="loading hidden" id="loading">
        <div class="spinner"></div>
    </div>

    <script>
        // 页面元素
        const currentPriceEl = document.getElementById('current-price');
        const updateTimeEl = document.getElementById('update-time');
        const refreshBtn = document.getElementById('refresh-btn');
        const loadingEl = document.getElementById('loading');
        const chartCanvas = document.getElementById('trend-chart');
        const chartPlaceholder = document.getElementById('chart-placeholder');
        
        // 价格数据API (需替换为实际数据URL)
        const PRICE_API_URL = 'https://ybdoc-1314621698.cos.ap-guangzhou.myqcloud.com/demo/price-data.json';
        
        // 图表初始配置
        const chartConfig = {
            type: 'line',
            data: {
                labels: ['5月10日', '5月11日', '5月12日', '5月13日', '5月14日', '5月15日', '今日'],
                datasets: [{
                    label: '铝锭价格',
                    data: [18200, 18150, 18180, 18220, 18190, 18240, null],
                    fill: false,
                    borderColor: '#1a73e8',
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '元';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                elements: {
                    point: {
                        radius: 4,
                        hoverRadius: 6,
                        backgroundColor: '#fff',
                        borderWidth: 2
                    }
                }
            }
        };
        
        // 初始化图表
        let trendChart = null;
        function initChart() {
            const ctx = chartCanvas.getContext('2d');
            trendChart = new Chart(ctx, chartConfig);
            chartPlaceholder.classList.add('hidden');
        }
        
        // 获取价格数据
        async function fetchPrice() {
            try {
                showLoading();
                const response = await fetch(`${PRICE_API_URL}?t=${new Date().getTime()}`);
                const data = await response.json();
                
                updatePriceDisplay(data);
                updateChartData(data.history);
                
                // 设置下一次自动刷新（5分钟）
                setTimeout(fetchPrice, 5 * 60 * 1000);
            } catch (error) {
                console.error('获取价格失败:', error);
                updatePriceDisplay({
                    price: "数据获取失败",
                    lastUpdated: new Date().toISOString()
                });
            } finally {
                hideLoading();
            }
        }
        
        // 更新价格显示
        function updatePriceDisplay(data) {
            const price = data.price || "--";
            const updateDate = new Date(data.lastUpdated || new Date());
            
            // 格式化时间：YYYY-MM-DD HH:MM
            const formattedTime = `${updateDate.getFullYear()}-${(updateDate.getMonth()+1).toString().padStart(2, '0')}-${updateDate.getDate().toString().padStart(2, '0')} ${updateDate.getHours().toString().padStart(2, '0')}:${updateDate.getMinutes().toString().padStart(2, '0')}`;
            
            // 价格趋势动画
            if (currentPriceEl.textContent !== "--") {
                const prevPrice = parseFloat(currentPriceEl.querySelector('span').textContent.replace(',', ''));
                const currentPrice = parseFloat(price.replace(',', ''));
                
                if (!isNaN(prevPrice) && !isNaN(currentPrice)) {
                    if (currentPrice > prevPrice) {
                        currentPriceEl.classList.add('price-up');
                        currentPriceEl.classList.remove('price-down');
                    } else if (currentPrice < prevPrice) {
                        currentPriceEl.classList.add('price-down');
                        currentPriceEl.classList.remove('price-up');
                    }
                }
            }
            
            // 更新DOM内容
            currentPriceEl.innerHTML = `<span class="loading-text">${price}</span><span class="price-unit">元/吨</span>`;
            updateTimeEl.textContent = formattedTime;
            
            // 添加动画效果
            currentPriceEl.classList.add('animate-fadeIn');
            setTimeout(() => {
                currentPriceEl.classList.remove('animate-fadeIn');
            }, 500);
        }
        
        // 更新图表数据
        function updateChartData(history) {
            if (!trendChart || !history) return;
            
            // 取最近7天数据
            const historyData = history.slice(-7);
            const dataPoints = historyData.map(item => parseFloat(item.price.replace(',', '')));
            
            // 更新图表
            trendChart.data.datasets[0].data = [...dataPoints.slice(0, -1), null];
            trendChart.update();
        }
        
        // 显示加载状态
        function showLoading() {
            loadingEl.classList.remove('hidden');
        }
        
        // 隐藏加载状态
        function hideLoading() {
            loadingEl.classList.add('hidden');
        }
        
        // 初始化页面
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化图表
            initChart();
            
            // 首次获取价格
            fetchPrice();
            
            // 绑定刷新按钮
            refreshBtn.addEventListener('click', fetchPrice);
        });
    </script>
    <!-- 引入Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</body>
</html>
