document.addEventListener('DOMContentLoaded', function () {

    // --- Register plugin ---
    try {
        Chart.register(ChartDataLabels);
    } catch (e) {
        console.error("Failed to register ChartDataLabels plugin.", e);
    }
    
    // --- Helper function for parsing LISTS ---
    function parseData(dataset) {
        if (!dataset) { return []; } 
        try {
            return JSON.parse(dataset.replace(/'/g, '"'));
        } catch (e) {
            console.error('Failed to parse JSON list data:', e, dataset);
            return [];
        }
    }

    // --- Chart 1: Target vs Realisasi (Bar) ---
    const ctx = document.getElementById('chartTargetRealisasi');
    if (ctx) {
        const labels = parseData(ctx.dataset.labels);
        const targetData = parseData(ctx.dataset.target);
        const realisasiData = parseData(ctx.dataset.realisasi);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels, 
                datasets: [
                    {
                        label: 'Target Paket',
                        data: targetData, 
                        backgroundColor: 'rgba(173, 216, 230, 0.6)',
                        borderColor: 'rgba(173, 216, 230, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Realisasi Paket (Partial)',
                        data: realisasiData, 
                        backgroundColor: 'rgba(0, 123, 255, 0.6)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: { 
                scales: { y: { beginAtZero: true } },
                plugins: { datalabels: { display: false } }
            }
        });
    }

    // --- Chart 2: Total JP (Line) ---
    const ctxJP = document.getElementById('chartTotalJP');
    if (ctxJP) {
        const labels = parseData(ctxJP.dataset.labels);
        const jpData = parseData(ctxJP.dataset.jp);
        
        new Chart(ctxJP, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Jam Pelajaran (JP)',
                    data: jpData,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: { 
                scales: { y: { beginAtZero: true } },
                plugins: { datalabels: { display: false } }
            }
        });
    }

    // --- Chart 3: Distribusi PIC (Doughnut) ---
    const ctxPIC = document.getElementById('chartPIC');
    if (ctxPIC) {
        const labels = parseData(ctxPIC.dataset.labels);
        const paketData = parseData(ctxPIC.dataset.paket);

        new Chart(ctxPIC, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Jumlah Paket',
                    data: paketData,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)', 'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)'
                    ],
                }]
            },
            options: {
                plugins: {
                    datalabels: {
                        formatter: (value, ctx) => {
                            const sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = (value * 100 / sum).toFixed(1) + '%';
                            return percentage;
                        },
                        color: '#fff',
                        font: { weight: 'bold', size: 12 }
                    }
                }
            }
        });
    }
    
    // --- Chart 4: Distribusi Kejuruan (Pie) ---
    const ctxKejuruan = document.getElementById('chartKejuruan');
    if (ctxKejuruan) {
        const labels = parseData(ctxKejuruan.dataset.labels);
        const paketData = parseData(ctxKejuruan.dataset.paket);

        new Chart(ctxKejuruan, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Jumlah Paket',
                    data: paketData,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)', 'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)', 'rgba(255, 206, 86, 0.7)'
                    ],
                }]
            },
            options: {
                plugins: {
                    datalabels: {
                        formatter: (value, ctx) => {
                            const sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = (value * 100 / sum).toFixed(1) + '%';
                            return percentage;
                        },
                        color: '#fff',
                        font: { weight: 'bold', size: 12 }
                    }
                }
            }
        });
    }

    // --- [MODIFIED] Chart 5: Rata-Rata Progress Keseluruhan (Bar) ---
    const ctxOverallProgress = document.getElementById('chartOverallProgress');
    if (ctxOverallProgress) {
        // Data is not a list, so we parse it directly as a float
        const uploadData = parseFloat(ctxOverallProgress.dataset.upload) || 0;
        const laporanData = parseFloat(ctxOverallProgress.dataset.laporan) || 0;

        new Chart(ctxOverallProgress, {
            type: 'bar',
            data: {
                // We define the labels directly here
                labels: ['Rata-Rata Upload', 'Rata-Rata Verifikasi'],
                datasets: [
                    {
                        label: 'Avg. Progress (%)',
                        data: [uploadData, laporanData], // The two data points
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.6)', // Blue
                            'rgba(75, 192, 192, 0.6)', // Green/Teal
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)',
                        ],
                        borderWidth: 1
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: { 
                        beginAtZero: true,
                        max: 100, // Progress is 0-100
                        ticks: {
                            callback: function(value) { return value + '%' }
                        }
                    }
                },
                plugins: {
                    datalabels: { // Show the value on top of the bar
                        anchor: 'end',
                        align: 'top',
                        formatter: (value) => value + '%',
                        font: { weight: 'bold' }
                    },
                    legend: {
                        display: false // Hide legend, labels are clear enough
                    }
                }
            }
        });
    }

    // --- Chart 6: Distribusi Status Pelatihan (Doughnut) ---
    const ctxStatusDist = document.getElementById('chartStatusDistribution');
    if (ctxStatusDist) {
        const labels = parseData(ctxStatusDist.dataset.labels);
        const countsData = parseData(ctxStatusDist.dataset.counts);

        new Chart(ctxStatusDist, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Jumlah Pelatihan',
                    data: countsData,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)', // Red-ish
                        'rgba(54, 162, 235, 0.7)', // Blue-ish
                        'rgba(75, 192, 192, 0.7)', // Green-ish
                        'rgba(153, 102, 255, 0.7)', // Purple-ish
                        'rgba(255, 159, 64, 0.7)'  // Orange-ish
                    ],
                }]
            },
            options: {
                plugins: {
                    datalabels: {
                        formatter: (value, ctx) => {
                            const sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = (value * 100 / sum).toFixed(1) + '%';
                            return `${value} (${percentage})`; 
                        },
                        color: '#fff',
                        font: { weight: 'bold', size: 12 }
                    }
                }
            }
        });
    }

});