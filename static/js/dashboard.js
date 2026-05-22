/**
 * TaskFlow Dashboard — Chart.js analytics
 */
(function () {
    'use strict';

    const dataEl = document.getElementById('dashboard-chart-data');
    if (!dataEl || typeof Chart === 'undefined') return;

    let chartData;
    try {
        chartData = JSON.parse(dataEl.textContent);
    } catch (e) {
        return;
    }

    const isDark = () => document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = () => (isDark() ? '#94a3b8' : '#64748b');
    const gridColor = () => (isDark() ? 'rgba(148,163,184,0.15)' : 'rgba(226,232,240,0.8)');

    const statusColors = ['#10b981', '#2563eb', '#94a3b8', '#ef4444'];
    const priorityColors = ['#10b981', '#f59e0b', '#ef4444'];

    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 800, easing: 'easeOutQuart' },
        plugins: {
            legend: {
                position: 'bottom',
                labels: { color: textColor(), padding: 12, usePointStyle: true, font: { size: 11 } }
            }
        }
    };

    const doughnutEl = document.getElementById('statusDoughnutChart');
    if (doughnutEl) {
        window.taskflowCharts = window.taskflowCharts || {};
        window.taskflowCharts.doughnut = new Chart(doughnutEl, {
            type: 'doughnut',
            data: {
                labels: chartData.statusLabels,
                datasets: [{
                    data: chartData.statusValues,
                    backgroundColor: statusColors,
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                ...baseOptions,
                cutout: '65%',
                plugins: {
                    ...baseOptions.plugins,
                    tooltip: { enabled: true }
                }
            }
        });
    }

    const barEl = document.getElementById('statusBarChart');
    if (barEl) {
        window.taskflowCharts.bar = new Chart(barEl, {
            type: 'bar',
            data: {
                labels: chartData.statusLabels,
                datasets: [{
                    label: 'Tasks',
                    data: chartData.statusValues,
                    backgroundColor: statusColors.map(c => c + 'cc'),
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                ...baseOptions,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: textColor(), font: { size: 10 } } },
                    y: { beginAtZero: true, grid: { color: gridColor() }, ticks: { color: textColor(), stepSize: 1 } }
                }
            }
        });
    }

    const priorityEl = document.getElementById('priorityChart');
    if (priorityEl) {
        window.taskflowCharts.priority = new Chart(priorityEl, {
            type: 'bar',
            data: {
                labels: chartData.priorityLabels,
                datasets: [{
                    label: 'By Priority',
                    data: chartData.priorityValues,
                    backgroundColor: priorityColors.map(c => c + 'cc'),
                    borderRadius: 8
                }]
            },
            options: {
                indexAxis: 'y',
                ...baseOptions,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: gridColor() }, ticks: { color: textColor() } },
                    y: { grid: { display: false }, ticks: { color: textColor() } }
                }
            }
        });
    }

    document.addEventListener('themeChanged', function () {
        [window.taskflowCharts.doughnut, window.taskflowCharts.bar, window.taskflowCharts.priority]
            .filter(Boolean)
            .forEach(chart => chart.update());
    });
})();
