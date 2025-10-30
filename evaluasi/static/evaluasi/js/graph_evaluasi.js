// evaluasi/static/evaluasi/js/graph_evaluasi.js

document.addEventListener('DOMContentLoaded', function () {

    // --- Helper function to parse data from canvas ---
    // Atribut data- dari HTML di-parse sebagai string, 
    // kita perlu mengubahnya kembali menjadi Array JavaScript.
    function parseData(dataset) {
        try {
            // Mengganti kutip tunggal (' yang dirender Django) dengan kutip ganda (") 
            // agar menjadi JSON yang valid.
            return JSON.parse(dataset.replace(/'/g, '"'));
        } catch (e) {
            console.error('Gagal mem-parsing data JSON dari atribut data-:', e, dataset);
            return [];
        }
    }

    // --- Grafik 1: Target vs Realisasi ---
    const ctx = document.getElementById('chartTargetRealisasi');
    if (ctx) {
        const labels = parseData(ctx.dataset.labels);
        const targetData = parseData(ctx.dataset.target);
        const realisasiData = parseData(ctx.dataset.realisasi);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels, // Gunakan data yang sudah di-parse
                datasets: [
                    {
                        label: 'Target Paket',
                        data: targetData, // Gunakan data yang sudah di-parse
                        backgroundColor: 'rgba(173, 216, 230, 0.6)',
                        borderColor: 'rgba(173, 216, 230, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Realisasi Paket',
                        data: realisasiData, // Gunakan data yang sudah di-parse
                        backgroundColor: 'rgba(0, 123, 255, 0.6)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: { scales: { y: { beginAtZero: true } } }
        });
    }

    // --- Grafik 2: Total JP ---
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
            options: { scales: { y: { beginAtZero: true } } }
        });
    }

    // --- Grafik 3: Distribusi PIC ---
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
        });
    }
    
    // --- Grafik 4: Distribusi Kejuruan ---
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
        });
    }
});