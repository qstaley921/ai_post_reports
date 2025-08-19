/**
 * AI Post Report - Vanilla JavaScript Module
 * Handles audio upload, processing, and field injection
 */

class AIPostReport {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000'; // FastAPI backend URL
        this.fileInput = document.getElementById('ai-audio-input');
        this.uploadBtn = document.getElementById('ai-audio-upload-btn');
        this.statusEl = document.getElementById('ai-status');
        this.errorEl = document.getElementById('ai-error');
        this.progressSteps = Array.from(document.querySelectorAll('#ai-progress .ai-step'));
        this.progressBar = document.getElementById('ai-progress-bar');
        
        this.isProcessing = false;
        this.abortController = null;
        
        this.init();
    }
    
    init() {
        // Store original step numbers for reset
        this.progressSteps.forEach(step => {
            const indicator = step.querySelector('.ai-step-indicator');
            if (indicator) {
                indicator.setAttribute('data-original', indicator.textContent.trim());
            }
        });
        
        // Event listeners
        this.uploadBtn.addEventListener('click', () => this.handleUploadClick());
        this.fileInput.addEventListener('change', () => this.handleFileSelect());
        
        this.updateStatus('No audio uploaded yet.');
    }
    
    handleUploadClick() {
        if (this.isProcessing) {
            this.abortProcessing();
        } else {
            this.fileInput.click();
        }
    }
    
    handleFileSelect() {
        const file = this.fileInput.files[0];
        if (!file) return;
        
        this.processAudioFile(file);
    }
    
    async processAudioFile(file) {
        try {
            this.isProcessing = true;
            this.updateUploadButton('Processing...', true);
            this.hideError();
            this.resetProgress();
            
            // Validate file
            if (!file.type.startsWith('audio/')) {
                throw new Error('Please select an audio file');
            }
            
            // Check file size (50MB limit)
            const maxSize = 50 * 1024 * 1024;
            if (file.size > maxSize) {
                throw new Error('File too large. Maximum size is 50MB');
            }
            
            this.updateStatus(`Processing ${file.name}...`);
            
            // Step 1: Upload and process
            this.setStepActive('upload');
            await this.uploadAndProcess(file);
            
        } catch (error) {
            this.handleError(error.message);
        } finally {
            this.isProcessing = false;
            this.updateUploadButton('Upload Audio File', false);
        }
    }
    
    async uploadAndProcess(file) {
        this.abortController = new AbortController();
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/post-report/audio`, {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.setStepComplete('upload');
            this.setStepActive('transcribe');
            
            const result = await response.json();
            
            this.setStepComplete('transcribe');
            this.setStepActive('organize');
            
            // Small delay to show organization step
            await new Promise(resolve => setTimeout(resolve, 500));
            
            this.setStepComplete('organize');
            this.setStepActive('pasting');
            
            // Inject the data into form fields
            this.injectReportData(result.report_data);
            
            this.setStepComplete('pasting');
            this.updateProgress(100);
            this.updateStatus('Audio processed successfully! Form fields have been updated.');
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.updateStatus('Upload cancelled');
            } else {
                throw error;
            }
        }
    }
    
    injectReportData(reportData) {
        if (!reportData || typeof reportData !== 'object') {
            console.warn('Invalid report data received:', reportData);
            return;
        }
        
        let fieldsUpdated = 0;
        
        Object.keys(reportData).forEach(fieldId => {
            const textarea = document.getElementById(fieldId);
            if (textarea && reportData[fieldId]) {
                // Preserve existing content if user prefers
                const existingContent = textarea.value.trim();
                if (existingContent) {
                    // Ask user if they want to replace existing content
                    const replace = confirm(`Field "${fieldId}" already has content. Replace it with AI-generated content?`);
                    if (!replace) return;
                }
                
                textarea.value = reportData[fieldId];
                fieldsUpdated++;
                
                // Visual feedback - briefly highlight the updated field
                textarea.style.backgroundColor = '#e8f5e8';
                setTimeout(() => {
                    textarea.style.backgroundColor = '';
                }, 2000);
            }
        });
        
        console.log(`Updated ${fieldsUpdated} form fields`);
    }
    
    setStepActive(stepName) {
        const step = document.querySelector(`.ai-step[data-step="${stepName}"]`);
        if (!step) return;
        
        const indicator = step.querySelector('.ai-step-indicator');
        indicator.style.borderColor = '#ffd700';
        indicator.style.color = '#ffd700';
        indicator.innerHTML = '<span class="fa fa-spinner fa-spin" style="font-size:10px;"></span>';
    }
    
    setStepComplete(stepName) {
        const step = document.querySelector(`.ai-step[data-step="${stepName}"]`);
        if (!step) return;
        
        const indicator = step.querySelector('.ai-step-indicator');
        indicator.style.borderColor = '#67b268';
        indicator.style.color = '#fff';
        indicator.style.background = '#67b268';
        indicator.innerHTML = '<span class="fa fa-check" style="font-size:12px;"></span>';
        
        // Update progress bar
        const stepIndex = this.progressSteps.findIndex(s => s.dataset.step === stepName);
        if (stepIndex >= 0) {
            const progress = ((stepIndex + 1) / this.progressSteps.length) * 100;
            this.updateProgress(progress);
        }
    }
    
    resetProgress() {
        this.progressSteps.forEach(step => {
            const indicator = step.querySelector('.ai-step-indicator');
            indicator.style.borderColor = '#888';
            indicator.style.color = '#888';
            indicator.style.background = '#222';
            indicator.textContent = indicator.getAttribute('data-original') || indicator.textContent;
        });
        this.updateProgress(0);
    }
    
    updateProgress(percentage) {
        this.progressBar.style.width = `${percentage}%`;
    }
    
    updateStatus(message) {
        this.statusEl.textContent = message;
    }
    
    updateUploadButton(text, disabled) {
        const span = this.uploadBtn.querySelector('span:last-child');
        if (span) span.textContent = text;
        this.uploadBtn.disabled = disabled;
        this.uploadBtn.style.opacity = disabled ? '0.7' : '1';
    }
    
    showError(message) {
        this.errorEl.textContent = message;
        this.errorEl.style.display = 'block';
    }
    
    hideError() {
        this.errorEl.style.display = 'none';
    }
    
    handleError(message) {
        console.error('AI Post Report Error:', message);
        this.showError(message);
        this.updateStatus('Error occurred during processing');
        this.resetProgress();
    }
    
    abortProcessing() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
        this.isProcessing = false;
        this.updateUploadButton('Upload Audio File', false);
        this.updateStatus('Processing cancelled');
        this.resetProgress();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if the AI post report elements exist
    if (document.getElementById('ai-post-report')) {
        window.aiPostReport = new AIPostReport();
    }
});

// Export for module use if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIPostReport;
}
