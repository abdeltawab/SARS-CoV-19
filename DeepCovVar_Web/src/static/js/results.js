// Results page JavaScript

// Get job ID from URL parameters
let pollInterval; // declare before any usage to avoid TDZ errors
const urlParams = new URLSearchParams(window.location.search);
const jobId = urlParams.get('job_id');

if (!jobId) {
    document.getElementById('loading_section').innerHTML = '<p style="color: #dc3545;">Error: No job ID provided</p>';
} else {
    document.getElementById('job_id').textContent = jobId;
    
    // Set up download links
    document.getElementById('download_csv').href = `/api/download/${jobId}/csv`;
    document.getElementById('download_excel').href = `/api/download/${jobId}/excel`;
    document.getElementById('download_pdf').href = `/api/download/${jobId}/pdf`;
    
    // Start polling for status
    pollJobStatus();
}


function pollJobStatus() {
    // Poll immediately
    checkStatus();
    
    // Then poll every 3 seconds
    pollInterval = setInterval(checkStatus, 3000);
}

async function checkStatus() {
    try {
        const response = await fetch(`/api/status/${jobId}`);
        const status = await response.json();
        
        if (response.ok) {
            updateStatusDisplay(status);
            
            if (status.status === 'completed') {
                clearInterval(pollInterval);
                loadResults();
            } else if (status.status === 'failed') {
                clearInterval(pollInterval);
                showError(status.error || 'Job failed');
            }
        } else {
            showError(status.error || 'Failed to fetch status');
        }
    } catch (error) {
        showError('Error checking job status: ' + error.message);
    }
}

function updateStatusDisplay(status) {
    // Update status badge
    const statusBadge = document.getElementById('status_badge');
    statusBadge.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
    statusBadge.className = 'status-badge status-' + status.status;
    
    // Update timestamp
    if (status.timestamp) {
        const date = new Date(status.timestamp);
        document.getElementById('timestamp').textContent = date.toLocaleString();
    }
    
    // Update progress
    if (status.status === 'running' || status.status === 'pending') {
        const progressContainer = document.getElementById('progress_container');
        progressContainer.style.display = 'block';
        
        const progressFill = document.getElementById('progress_fill');
        progressFill.style.width = status.progress + '%';
        progressFill.textContent = status.progress + '%';
        
        const progressMessage = document.getElementById('progress_message');
        progressMessage.textContent = status.message || 'Processing...';
    } else {
        document.getElementById('progress_container').style.display = 'none';
    }
}

async function loadResults() {
    try {
        const response = await fetch(`/api/results/${jobId}`);
        const results = await response.json();
        
        if (response.ok) {
            displayResults(results);
        } else {
            showError(results.error || 'Failed to load results');
        }
    } catch (error) {
        showError('Error loading results: ' + error.message);
    }
}

function displayResults(results) {
    // Hide loading, show results
    document.getElementById('loading_section').style.display = 'none';
    document.getElementById('results_section').style.display = 'block';
    
    // Update total sequences
    if (results.statistics_summary && results.statistics_summary.total_sequences) {
        document.getElementById('total_sequences').textContent = results.statistics_summary.total_sequences;
    }
    
    // Create visualizations
    if (results.statistics && Object.keys(results.statistics).length > 0) {
        createCharts(results.statistics);
    }
    
    // Create tables
    if (results.phases && Object.keys(results.phases).length > 0) {
        createTables(results.phases);
    }
}

function createCharts(statistics) {
    const chartsContainer = document.getElementById('charts_container');
    chartsContainer.innerHTML = '';
    
    // Create a chart for each phase
    Object.keys(statistics).forEach(phaseKey => {
        const phaseData = statistics[phaseKey];
        
        if (Object.keys(phaseData).length > 0) {
            const chartBox = document.createElement('div');
            chartBox.className = 'chart-box';
            
            const title = document.createElement('h3');
            title.className = 'chart-title';
            title.textContent = phaseKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            chartBox.appendChild(title);
            
            const canvas = document.createElement('canvas');
            canvas.id = `chart_${phaseKey}`;
            chartBox.appendChild(canvas);
            
            chartsContainer.appendChild(chartBox);
            
            // Create pie chart
            const labels = Object.keys(phaseData);
            const data = Object.values(phaseData);
            const colors = generateColors(labels.length);
            
            new Chart(canvas, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    aspectRatio: 1.2,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    });
}

function createTables(phases) {
    const tablesContainer = document.getElementById('results_tables');
    tablesContainer.innerHTML = '';
    
    Object.keys(phases).forEach(phaseKey => {
        const phaseData = phases[phaseKey];
        
        if (phaseData && phaseData.length > 0) {
            const phaseSection = document.createElement('div');
            phaseSection.style.marginBottom = '30px';
            
            const title = document.createElement('h3');
            title.textContent = phaseKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            title.style.color = '#6c5ce7';
            title.style.marginBottom = '15px';
            phaseSection.appendChild(title);
            
            const table = document.createElement('table');
            table.className = 'results-table';
            
            // Create header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            const columns = Object.keys(phaseData[0]);
            
            columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // Create body
            const tbody = document.createElement('tbody');
            
            // Show first 100 rows
            const rowsToShow = Math.min(phaseData.length, 100);
            for (let i = 0; i < rowsToShow; i++) {
                const row = document.createElement('tr');
                
                columns.forEach(col => {
                    const td = document.createElement('td');
                    td.textContent = phaseData[i][col] !== null ? phaseData[i][col] : '-';
                    row.appendChild(td);
                });
                
                tbody.appendChild(row);
            }
            
            table.appendChild(tbody);
            phaseSection.appendChild(table);
            
            if (phaseData.length > 100) {
                const note = document.createElement('p');
                note.style.marginTop = '10px';
                note.style.color = '#666';
                note.style.fontStyle = 'italic';
                note.textContent = `Showing first 100 of ${phaseData.length} results. Download full results using the buttons above.`;
                phaseSection.appendChild(note);
            }
            
            tablesContainer.appendChild(phaseSection);
        }
    });
}

function generateColors(count) {
    const colors = [
        '#28a745', '#007bff', '#dc3545', '#ffc107', '#17a2b8',
        '#6c757d', '#20c997', '#e83e8c', '#fd7e14', '#6610f2'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

function showError(message) {
    document.getElementById('loading_section').innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <p style="color: #dc3545; font-size: 1.2rem; font-weight: 600;">Error</p>
            <p style="color: #666; margin-top: 10px;">${message}</p>
            <a href="index.html" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 4px;">Return to Home</a>
        </div>
    `;
}
