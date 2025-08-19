/**
 * AI Post Report - Vanilla JavaScript Module
 * Handles audio upload, processing, and field injection
 */

console.log('AI Post Report JavaScript loaded successfully!');

class AIPostReport {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000'; // FastAPI backend URL
        this.fileInput = document.getElementById('ai-audio-file');
        this.uploadBtn = document.getElementById('ai-audio-upload-btn');
        this.statusEl = document.getElementById('ai-status');
        this.errorEl = document.getElementById('ai-error');
        this.progressBar = document.getElementById('ai-progress-bar');
        this.progressPercentage = document.getElementById('ai-progress-percentage');
        
        // Progress steps with new IDs
        this.progressSteps = {
            upload: document.getElementById('step-upload'),
            transcribe: document.getElementById('step-transcribe'),
            analyze: document.getElementById('step-analyze'),
            complete: document.getElementById('step-complete')
        };
        
        this.isProcessing = false;
        this.abortController = null;
        
        this.init();
    }
    
    init() {
        if (!this.uploadBtn || !this.fileInput) {
            console.error('Required AI Post Report elements not found');
            return;
        }
        
        // Event listeners
        this.uploadBtn.addEventListener('click', () => this.handleUploadClick());
        this.fileInput.addEventListener('change', () => this.handleFileSelect());
        
        this.updateStatus('No audio uploaded yet.');
        console.log('AI Post Report initialized successfully');
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
            this.updateUploadButton('Choose Audio File', false);
        }
    }
    
    async uploadAndProcess(file) {
        this.abortController = new AbortController();
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            // Step 1: Upload (25%)
            this.setStepActive('upload');
            this.updateProgress(25);
            this.updateStatus('Uploading audio file...');
            await this.simulateDelay(500); // Small delay for user feedback
            
            const response = await fetch(`${this.apiBaseUrl}/api/post-report/audio`, {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Step 2: Transcribe (50%)
            this.setStepActive('transcribe');
            this.updateProgress(50);
            this.updateStatus('Transcribing audio with AI... (Est. 30-60 seconds)');
            await this.simulateDelay(1500); // Simulate transcription time
            
            // Step 3: Analyze (75%)
            this.setStepActive('analyze');
            this.updateProgress(75);
            this.updateStatus('Analyzing content and organizing into report fields... (Est. 15-30 seconds)');
            await this.simulateDelay(1000); // Simulate analysis time
            
            const result = await response.json();
            
            // Step 4: Complete (100%)
            this.setStepActive('complete');
            this.updateProgress(100);
            this.updateStatus('Processing complete! Filling form fields...');
            
            // Inject the data into form fields
            this.injectReportData(result.report_data);
            
            this.updateStatus(`Audio processed successfully! Form fields have been updated. ${result.mode === 'demo' ? '(Demo Mode)' : ''}`);
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.updateStatus('Upload cancelled');
            } else {
                throw error;
            }
        }
    }
    
    async simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
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
        // Reset all steps
        Object.keys(this.progressSteps).forEach(key => {
            const step = this.progressSteps[key];
            if (step) {
                step.classList.remove('active');
            }
        });
        
        // Set current step active
        const currentStep = this.progressSteps[stepName];
        if (currentStep) {
            currentStep.classList.add('active');
        }
    }
    
    resetProgress() {
        // Reset all steps
        Object.keys(this.progressSteps).forEach(key => {
            const step = this.progressSteps[key];
            if (step) {
                step.classList.remove('active');
            }
        });
        
        this.updateProgress(0);
    }
    
    updateProgress(percentage) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percentage}%`;
        }
        if (this.progressPercentage) {
            this.progressPercentage.textContent = `${Math.round(percentage)}%`;
        }
    }
    
    updateStatus(message) {
        if (this.statusEl) {
            this.statusEl.textContent = message;
        }
    }
    
    updateUploadButton(text, disabled) {
        if (this.uploadBtn) {
            // Find the text node or span within the button
            const textNodes = Array.from(this.uploadBtn.childNodes).filter(node => 
                node.nodeType === Node.TEXT_NODE || node.tagName === 'SPAN'
            );
            
            if (textNodes.length > 0) {
                const lastTextNode = textNodes[textNodes.length - 1];
                if (lastTextNode.nodeType === Node.TEXT_NODE) {
                    lastTextNode.textContent = text;
                } else {
                    lastTextNode.textContent = text;
                }
            } else {
                // Fallback: just set the whole button text (this might override the icon)
                this.uploadBtn.innerHTML = `<i class="fas fa-microphone"></i> ${text}`;
            }
            
            this.uploadBtn.disabled = disabled;
            this.uploadBtn.style.opacity = disabled ? '0.7' : '1';
        }
    }
    
    showError(message) {
        if (this.errorEl) {
            this.errorEl.textContent = message;
            this.errorEl.style.display = 'block';
        }
    }
    
    hideError() {
        if (this.errorEl) {
            this.errorEl.style.display = 'none';
        }
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
        this.updateUploadButton('Choose Audio File', false);
        this.updateStatus('Processing cancelled');
        this.resetProgress();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if the AI post report elements exist
    if (document.getElementById('ai-audio-upload-btn')) {
        console.log('Initializing AI Post Report...');
        window.aiPostReport = new AIPostReport();
    } else {
        console.log('AI Post Report elements not found, checking again...');
        // Try again after a short delay in case elements are dynamically loaded
        setTimeout(() => {
            if (document.getElementById('ai-audio-upload-btn')) {
                console.log('AI Post Report elements found on retry, initializing...');
                window.aiPostReport = new AIPostReport();
            } else {
                console.log('AI Post Report elements still not found');
            }
        }, 100);
    }
});

// Export for module use if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIPostReport;
}
