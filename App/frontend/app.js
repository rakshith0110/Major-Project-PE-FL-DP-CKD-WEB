// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// Utility Functions
function showLoading(message = 'Initializing...') {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.add('active');
    updateProgress(0, message);
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function updateProgress(percentage, message) {
    document.getElementById('progressPercentage').textContent = `${percentage}%`;
    document.getElementById('progressBar').style.width = `${percentage}%`;
    document.getElementById('progressMessage').textContent = message;
}

async function pollProgress(operationId, onComplete) {
    const pollInterval = setInterval(async () => {
        try {
            const progress = await apiRequest(`/admin/progress/${operationId}`);
            
            updateProgress(progress.percentage, progress.message);
            
            if (progress.status === 'completed') {
                clearInterval(pollInterval);
                setTimeout(() => {
                    hideLoading();
                    if (onComplete) onComplete(progress);
                }, 500);
            } else if (progress.status === 'failed') {
                clearInterval(pollInterval);
                hideLoading();
                showToast(progress.message, 'error');
            }
        } catch (error) {
            console.error('Progress polling error:', error);
        }
    }, 500); // Poll every 500ms
    
    return pollInterval;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();
    
    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            await loadCurrentUser();
            showDashboard();
            showToast('Login successful!', 'success');
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Login failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

async function loadCurrentUser() {
    try {
        currentUser = await apiRequest('/auth/me');
        document.getElementById('userFullName').textContent = currentUser.full_name || currentUser.username;
        document.getElementById('userRole').textContent = currentUser.role.toUpperCase();
        
        // Show/hide admin-only items
        const adminItems = document.querySelectorAll('.admin-only');
        adminItems.forEach(item => {
            item.style.display = currentUser.role === 'admin' ? 'flex' : 'none';
        });
    } catch (error) {
        console.error('Failed to load user:', error);
        logout();
    }
}

function showDashboard() {
    document.getElementById('loginPage').classList.remove('active');
    document.getElementById('dashboardPage').classList.add('active');
    loadDashboardData();
}

function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    document.getElementById('dashboardPage').classList.remove('active');
    document.getElementById('loginPage').classList.add('active');
    document.getElementById('loginForm').reset();
}

document.getElementById('logoutBtn')?.addEventListener('click', logout);

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.dataset.page;
        
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        // Update active content section
        document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
        document.getElementById(`${page}Content`).classList.add('active');
        
        // Update page title
        const titles = {
            'overview': 'Dashboard Overview',
            'clients': 'Manage Clients',
            'training': 'Client Training',
            'predictions': 'Make Predictions',
            'global-model': 'Global Model Management',
            'aggregation': 'Federated Aggregation'
        };
        document.getElementById('pageTitle').textContent = titles[page];
        
        // Load page-specific data
        loadPageData(page);
    });
});

async function loadPageData(page) {
    switch(page) {
        case 'overview':
            await loadDashboardData();
            break;
        case 'clients':
            await loadClients();
            break;
        case 'training':
            await loadClientsForTraining();
            break;
        case 'predictions':
            await loadClientsForPrediction();
            await loadPredictionHistory();
            break;
        case 'global-model':
            await loadGlobalModels();
            break;
        case 'aggregation':
            await loadClientsForAggregation();
            await loadClientStats();
            break;
    }
}

// Dashboard Data
async function loadDashboardData() {
    try {
        if (currentUser?.role === 'admin') {
            const stats = await apiRequest('/admin/dashboard-stats');
            document.getElementById('totalClients').textContent = stats.total_clients;
            document.getElementById('activeClients').textContent = stats.active_clients;
            document.getElementById('totalTrainings').textContent = stats.total_trainings;
            document.getElementById('totalPredictions').textContent = stats.total_predictions;
            document.getElementById('globalAccuracy').textContent = stats.global_model_accuracy ? 
                (stats.global_model_accuracy * 100).toFixed(2) + '%' : 'N/A';
            document.getElementById('globalAuc').textContent = stats.global_model_auc ? 
                stats.global_model_auc.toFixed(4) : 'N/A';
        }
        
        // Load recent activity
        const logs = await apiRequest('/admin/training-logs');
        const activityHtml = logs.slice(0, 5).map(log => `
            <div class="activity-item">
                <strong>${log.training_type}</strong> - ${log.status}
                <br><small>${new Date(log.started_at).toLocaleString()}</small>
            </div>
        `).join('');
        document.getElementById('recentActivity').innerHTML = activityHtml || '<p class="text-muted">No recent activity</p>';
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

// Clients Management
async function loadClients() {
    try {
        const clients = await apiRequest('/clients/');
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Client Name</th>
                        <th>Status</th>
                        <th>Dataset</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${clients.map(client => `
                        <tr>
                            <td>${client.client_name}</td>
                            <td><span class="badge badge-${client.is_active ? 'success' : 'danger'}">
                                ${client.is_active ? 'Active' : 'Inactive'}
                            </span></td>
                            <td>${client.dataset_path ? '✓ Uploaded' : '✗ Not uploaded'}</td>
                            <td>${new Date(client.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="uploadDataset(${client.id})">
                                    <i class="fas fa-upload"></i> Upload
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('clientsList').innerHTML = html;
    } catch (error) {
        showToast('Failed to load clients', 'error');
    }
}

document.getElementById('addClientBtn')?.addEventListener('click', () => {
    document.getElementById('addClientModal').classList.add('active');
});

document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.modal').forEach(modal => modal.classList.remove('active'));
    });
});

document.getElementById('addClientForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();
    
    try {
        const clientName = document.getElementById('clientName').value;
        const client = await apiRequest('/clients/', {
            method: 'POST',
            body: JSON.stringify({ client_name: clientName })
        });
        
        // Upload dataset if provided
        const fileInput = document.getElementById('datasetFile');
        if (fileInput.files.length > 0) {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            await fetch(`${API_BASE_URL}/clients/${client.id}/upload-dataset`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}` },
                body: formData
            });
        }
        
        showToast('Client created successfully!', 'success');
        document.getElementById('addClientModal').classList.remove('active');
        document.getElementById('addClientForm').reset();
        await loadClients();
    } catch (error) {
        showToast('Failed to create client: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

async function uploadDataset(clientId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        showLoading();
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE_URL}/clients/${clientId}/upload-dataset`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}` },
                body: formData
            });
            
            if (response.ok) {
                showToast('Dataset uploaded successfully!', 'success');
                await loadClients();
            } else {
                const data = await response.json();
                showToast('Upload failed: ' + data.detail, 'error');
            }
        } catch (error) {
            showToast('Upload failed: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    };
    input.click();
}

// Training
async function loadClientsForTraining() {
    try {
        const clients = await apiRequest('/clients/');
        const select = document.getElementById('trainingClientId');
        select.innerHTML = '<option value="">-- Select Client --</option>' +
            clients.map(c => `<option value="${c.id}">${c.client_name}</option>`).join('');
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

document.getElementById('clientTrainingForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();
    
    try {
        const clientId = parseInt(document.getElementById('trainingClientId').value);
        const result = await apiRequest(`/clients/${clientId}/train`, {
            method: 'POST',
            body: JSON.stringify({
                client_id: clientId,
                local_epochs: parseInt(document.getElementById('localEpochs').value),
                batch_size: parseInt(document.getElementById('batchSize').value),
                learning_rate: parseFloat(document.getElementById('learningRate').value),
                max_grad_norm: 1.0,
                noise_multiplier: 0.8
            })
        });
        
        showToast('Training completed successfully!', 'success');
        await loadTrainingHistory(clientId);
    } catch (error) {
        showToast('Training failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

async function loadTrainingHistory(clientId) {
    if (!clientId) return;
    
    try {
        const history = await apiRequest(`/clients/${clientId}/training-history`);
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Accuracy</th>
                        <th>F1 Score</th>
                        <th>AUC</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${history.map(log => `
                        <tr>
                            <td><span class="badge badge-${log.status === 'completed' ? 'success' : 'danger'}">
                                ${log.status}
                            </span></td>
                            <td>${log.accuracy ? (log.accuracy * 100).toFixed(2) + '%' : 'N/A'}</td>
                            <td>${log.f1_score ? log.f1_score.toFixed(4) : 'N/A'}</td>
                            <td>${log.auc ? log.auc.toFixed(4) : 'N/A'}</td>
                            <td>${new Date(log.started_at).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('trainingHistory').innerHTML = html;
    } catch (error) {
        console.error('Failed to load training history:', error);
    }
}

// Predictions
async function loadClientsForPrediction() {
    try {
        const clients = await apiRequest('/clients/');
        const select = document.getElementById('predictionClientId');
        select.innerHTML = '<option value="">-- Select Client --</option>' +
            clients.map(c => `<option value="${c.id}">${c.client_name}</option>`).join('');
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

document.getElementById('predictionForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();
    
    try {
        const clientId = parseInt(document.getElementById('predictionClientId').value);
        const patientData = {
            age: parseFloat(document.getElementById('age').value),
            bp: parseFloat(document.getElementById('bp').value),
            sg: parseFloat(document.getElementById('sg').value)
            // Add more fields as needed
        };
        
        const result = await apiRequest('/predictions/', {
            method: 'POST',
            body: JSON.stringify({
                client_id: clientId,
                patient_data: patientData
            })
        });
        
        // Show result
        const resultDiv = document.getElementById('predictionResult');
        const outputDiv = document.getElementById('predictionOutput');
        
        const resultClass = result.prediction_label === 'YES' ? 'danger' : 'success';
        outputDiv.innerHTML = `
            <div class="metric-row">
                <span>Prediction:</span>
                <strong class="badge badge-${resultClass}">${result.prediction_label}</strong>
            </div>
            <div class="metric-row">
                <span>Probability:</span>
                <strong>${(result.prediction_probability * 100).toFixed(2)}%</strong>
            </div>
            <div class="metric-row">
                <span>Class:</span>
                <strong>${result.prediction_class}</strong>
            </div>
        `;
        resultDiv.style.display = 'block';
        
        showToast('Prediction completed!', 'success');
        await loadPredictionHistory();
    } catch (error) {
        showToast('Prediction failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

async function loadPredictionHistory() {
    try {
        const predictions = await apiRequest('/predictions/');
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Result</th>
                        <th>Probability</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${predictions.slice(0, 10).map(pred => `
                        <tr>
                            <td><span class="badge badge-${pred.prediction_label === 'YES' ? 'danger' : 'success'}">
                                ${pred.prediction_label}
                            </span></td>
                            <td>${(pred.prediction_probability * 100).toFixed(2)}%</td>
                            <td>${new Date(pred.created_at).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('predictionHistory').innerHTML = html;
    } catch (error) {
        console.error('Failed to load prediction history:', error);
    }
}

// Global Model (Admin)
document.getElementById('globalModelForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading('Starting global model training...');
    
    try {
        const response = await apiRequest('/admin/init-global-model', {
            method: 'POST',
            body: JSON.stringify({
                epochs: parseInt(document.getElementById('globalEpochs').value),
                batch_size: parseInt(document.getElementById('globalBatchSize').value),
                learning_rate: parseFloat(document.getElementById('globalLearningRate').value)
            })
        });
        
        // Start polling for progress
        await pollProgress(response.operation_id, async () => {
            showToast('Global model initialized successfully!', 'success');
            await loadGlobalModels();
        });
    } catch (error) {
        hideLoading();
        showToast('Failed to initialize global model: ' + error.message, 'error');
    }
});

async function loadGlobalModels() {
    try {
        const models = await apiRequest('/admin/global-models');
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Round</th>
                        <th>Accuracy</th>
                        <th>AUC</th>
                        <th>Clients</th>
                        <th>Status</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${models.map(model => `
                        <tr>
                            <td>${model.round_number}</td>
                            <td>${model.accuracy ? (model.accuracy * 100).toFixed(2) + '%' : 'N/A'}</td>
                            <td>${model.auc ? model.auc.toFixed(4) : 'N/A'}</td>
                            <td>${model.num_clients}</td>
                            <td><span class="badge badge-${model.is_current ? 'success' : 'info'}">
                                ${model.is_current ? 'Current' : 'Historical'}
                            </span></td>
                            <td>${new Date(model.created_at).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('globalModelsList').innerHTML = html;
    } catch (error) {
        console.error('Failed to load global models:', error);
    }
}

// Aggregation (Admin)
async function loadClientsForAggregation() {
    try {
        const clients = await apiRequest('/clients/');
        const html = clients.map(client => `
            <div class="checkbox-item">
                <input type="checkbox" id="client_${client.id}" value="${client.id}">
                <label for="client_${client.id}">${client.client_name}</label>
            </div>
        `).join('');
        document.getElementById('clientsCheckboxList').innerHTML = html;
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

document.getElementById('aggregationForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const checkboxes = document.querySelectorAll('#clientsCheckboxList input[type="checkbox"]:checked');
    const clientIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (clientIds.length === 0) {
        showToast('Please select at least one client', 'warning');
        return;
    }
    
    showLoading('Starting federated aggregation...');
    
    try {
        const response = await apiRequest('/admin/aggregate', {
            method: 'POST',
            body: JSON.stringify({ client_ids: clientIds })
        });
        
        // Start polling for progress
        await pollProgress(response.operation_id, async () => {
            showToast('Aggregation completed successfully!', 'success');
            await loadClientStats();
        });
    } catch (error) {
        hideLoading();
        showToast('Aggregation failed: ' + error.message, 'error');
    }
});

async function loadClientStats() {
    try {
        const stats = await apiRequest('/admin/client-stats');
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Client</th>
                        <th>Trainings</th>
                        <th>Latest Accuracy</th>
                        <th>Latest AUC</th>
                        <th>Predictions</th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.map(stat => `
                        <tr>
                            <td>${stat.client_name}</td>
                            <td>${stat.total_trainings}</td>
                            <td>${stat.latest_accuracy ? (stat.latest_accuracy * 100).toFixed(2) + '%' : 'N/A'}</td>
                            <td>${stat.latest_auc ? stat.latest_auc.toFixed(4) : 'N/A'}</td>
                            <td>${stat.total_predictions}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('clientStats').innerHTML = html;
    } catch (error) {
        console.error('Failed to load client stats:', error);
    }
}

// Refresh button
document.getElementById('refreshBtn')?.addEventListener('click', () => {
    const activePage = document.querySelector('.nav-item.active')?.dataset.page;
    if (activePage) {
        loadPageData(activePage);
    }
});

// Initialize
if (authToken) {
    loadCurrentUser().then(() => {
        showDashboard();
    }).catch(() => {
        logout();
    });
}

// Made with Bob
