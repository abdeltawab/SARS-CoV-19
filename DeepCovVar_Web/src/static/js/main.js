// Main JavaScript for DeepCovVar Web Application

// DOM Elements
const fileUpload = document.getElementById('file_upload');
const fileName = document.getElementById('file_name');
const loadDemoBtn = document.getElementById('load_demo');
const selectAllPhasesBtn = document.getElementById('select_all_phases');
const resetBtn = document.getElementById('reset_button');
const runPredictionBtn = document.getElementById('run_prediction');
const statusMessage = document.getElementById('status_message');
const sequenceText = document.getElementById('sequence_text');
const accessionId = document.getElementById('accession_id');

// File upload handler
fileUpload.addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        fileName.textContent = e.target.files[0].name;
    } else {
        fileName.textContent = 'Choose file';
    }
});

// Load demo FASTA
loadDemoBtn.addEventListener('click', async function() {
    try {
        const response = await fetch('/demo/demo.fasta');
        const demoData = await response.text();
        sequenceText.value = demoData;
        showStatus('Demo FASTA loaded successfully', 'success');
    } catch (error) {
        showStatus('Failed to load demo FASTA', 'error');
    }
});

// Select all phases
selectAllPhasesBtn.addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('input[name="phases"]');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
    
    this.textContent = allChecked ? 'Select All Phases' : 'Deselect All Phases';
    updateThresholdControls();
});

// Threshold controls functionality
function updateThresholdControls() {
    const thresholdControls = document.getElementById('threshold_controls');
    const phaseCheckboxes = document.querySelectorAll('input[name="phases"]');
    const binaryPhases = ['1', '2', '3']; // Phases that support thresholds
    
    const selectedBinaryPhases = Array.from(phaseCheckboxes)
        .filter(cb => cb.checked && binaryPhases.includes(cb.value));
    
    if (selectedBinaryPhases.length > 0) {
        thresholdControls.style.display = 'block';
    } else {
        thresholdControls.style.display = 'none';
    }
}

// Reset thresholds to defaults
document.getElementById('reset_thresholds').addEventListener('click', function() {
    const thresholdInputs = document.querySelectorAll('.threshold-input-field');
    thresholdInputs.forEach(input => {
        input.value = '50';
    });
    showStatus('Thresholds reset to default values (50%)', 'success');
});

// Listen for phase selection changes
document.querySelectorAll('input[name="phases"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateThresholdControls);
});

// Reset form
resetBtn.addEventListener('click', function() {
    // Reset all form inputs
    document.querySelectorAll('input[type="text"], input[type="email"], textarea').forEach(input => {
        input.value = '';
    });
    
    // Reset file input
    fileUpload.value = '';
    fileName.textContent = 'Choose file';
    
    // Reset checkboxes
    document.querySelectorAll('input[name="phases"]').forEach(cb => {
        cb.checked = false;
    });
    
    // Reset radio buttons to defaults
    document.querySelector('input[name="sequence_type"][value="protein"]').checked = true;
    document.querySelector('input[name="database"][value="ncbi"]').checked = true;
    
    // Reset threshold controls
    document.querySelectorAll('.threshold-input-field').forEach(input => {
        input.value = '50';
    });
    document.getElementById('threshold_controls').style.display = 'none';
    
    // Hide status message
    hideStatus();
    
    selectAllPhasesBtn.textContent = 'Select All Phases';
});

// Run prediction
runPredictionBtn.addEventListener('click', async function() {
    try {
        // Validate input
        const hasFile = fileUpload.files.length > 0;
        const hasText = sequenceText.value.trim() !== '';
        const hasAccession = accessionId.value.trim() !== '';
        
        if (!hasFile && !hasText && !hasAccession) {
            showStatus('Please provide input: upload a file, paste sequences, or enter an accession ID', 'error');
            return;
        }
        
        // Check if at least one phase is selected
        const selectedPhases = Array.from(document.querySelectorAll('input[name="phases"]:checked'));
        if (selectedPhases.length === 0) {
            showStatus('Please select at least one prediction phase', 'error');
            return;
        }
        
        // Prepare form data
        const formData = new FormData();
        
        // Add sequence type
        const sequenceType = document.querySelector('input[name="sequence_type"]:checked').value;
        formData.append('sequence_type', sequenceType);
        
        // Add phases
        selectedPhases.forEach(phase => {
            formData.append('phases[]', phase.value);
        });
        
        // Add thresholds for binary classification phases
        const binaryPhases = ['1', '2', '3'];
        selectedPhases.forEach(phase => {
            if (binaryPhases.includes(phase.value)) {
                const phaseNum = phase.value;
                const threshold1 = document.getElementById(`phase${phaseNum}_threshold1`).value;
                const threshold2 = document.getElementById(`phase${phaseNum}_threshold2`).value;
                formData.append(`phase${phaseNum}_thresholds`, `${threshold1},${threshold2}`);
            }
        });
        
        // Use optimized models by default
        formData.append('model_type', 'optimized');
        formData.append('verbose', false);
        
        // Add email if provided
        const email = document.getElementById('email').value.trim();
        if (email) {
            formData.append('email', email);
        }
        
        // Add input based on what's provided
        if (hasFile) {
            formData.append('file', fileUpload.files[0]);
        } else if (hasText) {
            formData.append('sequence_text', sequenceText.value);
        } else if (hasAccession) {
            const database = document.querySelector('input[name="database"]:checked').value;
            formData.append('accession_id', accessionId.value.trim());
            formData.append('database', database);
        }
        
        // Disable button and show loading status
        runPredictionBtn.disabled = true;
        runPredictionBtn.textContent = 'Submitting...';
        showStatus('Submitting prediction job...', 'info');
        
        // Submit prediction
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showStatus('Job submitted successfully! Job ID: ' + result.job_id, 'success');
            
            // Redirect to results page after a short delay
            setTimeout(() => {
                window.location.href = `results.html?job_id=${result.job_id}`;
            }, 2000);
        } else {
            showStatus('Error: ' + (result.error || 'Unknown error occurred'), 'error');
            runPredictionBtn.disabled = false;
            runPredictionBtn.textContent = 'Run Prediction';
        }
        
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
        runPredictionBtn.disabled = false;
        runPredictionBtn.textContent = 'Run Prediction';
    }
});

// Helper function to show status message
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = 'status-message ' + type;
    statusMessage.style.display = 'block';
}

// Helper function to hide status message
function hideStatus() {
    statusMessage.style.display = 'none';
}

// Update select all phases button text based on checkbox state
document.querySelectorAll('input[name="phases"]').forEach(cb => {
    cb.addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('input[name="phases"]');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        selectAllPhasesBtn.textContent = allChecked ? 'Deselect All Phases' : 'Select All Phases';
    });
});
