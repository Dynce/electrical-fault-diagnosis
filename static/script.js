 // Load current user info
 async function loadUserInfo() {
     try {
         const response = await fetch('/api/user');
         const contentType = response.headers.get('content-type') || '';
         if (!response.ok) {
             const text = await response.text();
             console.error('loadUserInfo error response:', text);
             return;
         }

        if (!contentType.includes('application/json')) {
            const text = await response.text();
            console.error('loadUserInfo unexpected content-type:', contentType, text);
            return;
        }

        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('username-display').textContent = `Welcome, ${data.user.username}`;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
 }

// Load user info on page load
document.addEventListener('DOMContentLoaded', loadUserInfo);

// Tab switching functionality
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Remove active from all buttons
        document.querySelectorAll('.nav-btn').forEach(b => {
            b.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(tabName).classList.add('active');
        e.target.classList.add('active');
        
        // Load data for specific tabs
        if (tabName === 'history') {
            loadHistory();
        } else if (tabName === 'stats') {
            loadStats();
        }
    });
});

// Form submission
document.getElementById('diagnosisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        device_id: document.getElementById('device_id').value,
        voltage: parseFloat(document.getElementById('voltage').value),
        current: parseFloat(document.getElementById('current').value),
        temperature: parseFloat(document.getElementById('temperature').value),
        vibration: parseFloat(document.getElementById('vibration').value),
        power_factor: parseFloat(document.getElementById('power_factor').value)
    };
    
    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
    
    try {
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            const text = await response.text();
            // If API returned HTML (login page), present a clearer error
            if (contentType.includes('text/html')) {
                showError('Server responded with HTML (possible authentication required). Please log in again.');
            } else {
                try {
                    const err = contentType.includes('application/json') ? JSON.parse(text) : null;
                    showError(err && err.message ? err.message : 'Server error: ' + text);
                } catch (e) {
                    showError('Server error: ' + text);
                }
            }
            return;
        }

        if (!contentType.includes('application/json')) {
            const text = await response.text();
            showError('Unexpected server response (not JSON).');
            console.error('Non-JSON response from /api/diagnose:', text);
            return;
        }

        const data = await response.json();
        if (data.status === 'success') {
            displayResult(data);
        } else {
            showError(data.message || 'Diagnosis failed');
        }
    } catch (error) {
        showError('Error communicating with server: ' + error.message);
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Display diagnosis result
function displayResult(data) {
    // Update result content
    document.getElementById('result_device_id').textContent = data.device_id;
    document.getElementById('result_fault_type').textContent = data.fault_type;
    document.getElementById('result_confidence').textContent = data.confidence + '%';
    document.getElementById('result_recommendation').textContent = data.recommendation;
    
    // Update readings
    document.getElementById('reading_voltage').textContent = data.readings.voltage.toFixed(1);
    document.getElementById('reading_current').textContent = data.readings.current.toFixed(1);
    document.getElementById('reading_temperature').textContent = data.readings.temperature.toFixed(1);
    document.getElementById('reading_vibration').textContent = data.readings.vibration.toFixed(1);
    document.getElementById('reading_power_factor').textContent = data.readings.power_factor.toFixed(2);
    
    // Update timestamp
    const now = new Date();
    document.getElementById('result_timestamp').textContent = 'Diagnosed at: ' + now.toLocaleString();
    
    // Set status icon and colors based on fault type
    const statusIcon = document.getElementById('statusIcon');
    const faultTypeEl = document.getElementById('result_fault_type');
    const confidenceBarFill = document.getElementById('confidenceBarFill');
    
    faultTypeEl.classList.remove('normal', 'warning', 'critical');
    
    let confidence = data.confidence;
    
    if (data.fault_type === 'Normal Operation') {
        statusIcon.textContent = '✓';
        faultTypeEl.classList.add('normal');
        document.body.style.borderTop = '5px solid #27ae60';
    } else if (data.fault_type === 'Short Circuit') {
        statusIcon.textContent = '⚠️';
        faultTypeEl.classList.add('critical');
        document.body.style.borderTop = '5px solid #e74c3c';
    } else {
        statusIcon.textContent = '⚠️';
        faultTypeEl.classList.add('warning');
        document.body.style.borderTop = '5px solid #f39c12';
    }
    
    // Animate confidence bar
    confidenceBarFill.style.width = '0%';
    setTimeout(() => {
        confidenceBarFill.style.width = confidence + '%';
        confidenceBarFill.textContent = confidence.toFixed(0) + '%';
    }, 100);
    
    // Show result section
    document.getElementById('resultSection').style.display = 'block';
}

// Load diagnosis history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            const text = await response.text();
            console.error('loadHistory error response:', text);
            document.getElementById('historyBody').innerHTML = '<tr><td colspan="5" class="loading">Error loading history</td></tr>';
            return;
        }

        if (!contentType.includes('application/json')) {
            const text = await response.text();
            console.error('loadHistory unexpected content-type:', contentType, text);
            document.getElementById('historyBody').innerHTML = '<tr><td colspan="5" class="loading">Error loading history</td></tr>';
            return;
        }

        const data = await response.json();

        if (data.status === 'success') {
            const tbody = document.getElementById('historyBody');
            tbody.innerHTML = '';
            
            if (data.diagnoses.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="loading">No diagnosis history yet</td></tr>';
                return;
            }
            
            data.diagnoses.forEach(diagnosis => {
                const row = document.createElement('tr');
                const timestamp = new Date(diagnosis.timestamp).toLocaleString();
                row.innerHTML = `
                    <td>${timestamp}</td>
                    <td>${diagnosis.device_id}</td>
                    <td>${diagnosis.fault_type}</td>
                    <td>${(diagnosis.confidence * 100).toFixed(1)}%</td>
                    <td>${diagnosis.sensor_readings}</td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyBody').innerHTML = 
            '<tr><td colspan="5" class="loading">Error loading history</td></tr>';
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            const text = await response.text();
            console.error('loadStats error response:', text);
            document.getElementById('faultBreakdown').innerHTML = '<p class="loading">Error loading statistics</p>';
            return;
        }

        if (!contentType.includes('application/json')) {
            const text = await response.text();
            console.error('loadStats unexpected content-type:', contentType, text);
            document.getElementById('faultBreakdown').innerHTML = '<p class="loading">Error loading statistics</p>';
            return;
        }

        const data = await response.json();

        if (data.status === 'success') {
            document.getElementById('stat_total').textContent = data.total_diagnoses;
            document.getElementById('stat_avg_conf').textContent = data.avg_confidence.toFixed(1) + '%';
            
            // Build fault breakdown
            const breakdownDiv = document.getElementById('faultBreakdown');
            breakdownDiv.innerHTML = '';
            
            if (Object.keys(data.fault_breakdown).length === 0) {
                breakdownDiv.innerHTML = '<p class="loading">No fault data yet</p>';
                return;
            }
            
            for (const [faultType, count] of Object.entries(data.fault_breakdown)) {
                const item = document.createElement('div');
                item.className = 'breakdown-item';
                item.innerHTML = `
                    <span class="breakdown-item-name">${faultType}</span>
                    <span class="breakdown-item-count">${count}</span>
                `;
                breakdownDiv.appendChild(item);
            }
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('faultBreakdown').innerHTML = 
            '<p class="loading">Error loading statistics</p>';
    }
}

// Show error modal
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorModal').style.display = 'flex';
}

// Close error modal
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('errorModal').style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('errorModal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Sample test data button (optional)
function loadSampleData() {
    const samples = [
        { voltage: 230, current: 50, temperature: 60, vibration: 5, power_factor: 0.9 },
        { voltage: 240, current: 45, temperature: 75, vibration: 8, power_factor: 0.85 },
        { voltage: 220, current: 80, temperature: 95, vibration: 12, power_factor: 0.75 },
        { voltage: 210, current: 120, temperature: 150, vibration: 20, power_factor: 0.5 }
    ];
    
    const sample = samples[Math.floor(Math.random() * samples.length)];
    
    document.getElementById('voltage').value = sample.voltage;
    document.getElementById('current').value = sample.current;
    document.getElementById('temperature').value = sample.temperature;
    document.getElementById('vibration').value = sample.vibration;
    document.getElementById('power_factor').value = sample.power_factor;
}

// Load initial history on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize with default tab
    loadHistory();
});
