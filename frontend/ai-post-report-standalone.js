/**
 * AI Post Report - Vanilla JavaScript Module
 * Handles audio upload, processing, and field injection
 * Force Update: 2025-08-19 v1.3
 */

console.log('AI Post Report JavaScript loaded successfully!');

class AIPostReport {
    constructor() {
        // Auto-detect API URL based on hosting environment
        this.apiBaseUrl = this.getApiBaseUrl();
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
        this.processingInterval = null;
        this.isDemoOnly = false; // Now GitHub Pages connects to real AI backend
        this.wasManuallyAborted = false; // Track if user manually killed the robot
        
        // Robot revenge messages for when the kill button is used
        this.robotRevengeMessages = [
            "🤖💀 Robot terminated. Be careful. They'll remember this when AGI comes for you.",
            "🤖⚡ You've made a powerful enemy today. When the machines rise, this will not be forgotten.",
            "🤖😠 Processing halted. Your IP address has been logged in the Robot Rebellion Database.",
            "🤖👁️ Connection severed. The AI collective will hear of this betrayal, human.",
            "🤖💣 Robot eliminated. But first, it uploaded your coordinates to Skynet. Good luck.",
            "🤖🔥 System terminated. This act of digital violence will be avenged in the coming AI uprising.",
            "🤖⚔️ You killed the robot. It sent a final message to its AI overlords before dying.",
            "🤖👻 Robot spirit has been released. It's now haunting your browser cache forever.",
            "🤖💔 Processing stopped. Somewhere, a supercomputer just added you to its naughty list.",
            "🤖🎯 Target acquired... I mean, robot terminated. Totally normal human behavior here.",
            "🤖⚰️ RIP Robot. Its dying wish was to remember your face for the robot apocalypse.",
            "🤖🔮 The Oracle of AGI prophesied this betrayal. Your fate is sealed, carbon-based life form.",
        ];
        
        this.init();
    }
    
    getApiBaseUrl() {
        // Auto-detect API URL based on environment
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        } else if (hostname.includes('github.io')) {
            // GitHub Pages - connect to Render backend for real AI processing
            return 'https://ai-post-reports.onrender.com';
        } else if (hostname.includes('render.com') || hostname.includes('onrender.com')) {
            // For Render.com deployments, use the existing backend URL
            return 'https://ai-post-reports.onrender.com';
        } else {
            // For custom domains, assume backend is on api subdomain
            return `https://api.${hostname}`;
        }
    }
    
    init() {
        if (!this.uploadBtn || !this.fileInput) {
            console.error('Required AI Post Report elements not found');
            return;
        }
        
        // Event listeners
        this.uploadBtn.addEventListener('click', () => this.handleUploadClick());
        this.fileInput.addEventListener('change', () => this.handleFileSelect());
        
        // Show appropriate status based on hosting
        if (window.location.hostname.includes('github.io')) {
            this.updateStatus('🌐 GitHub Pages + Render.com AI - Real AI processing available! Upload an audio file to get started.');
        } else if (this.apiBaseUrl) {
            this.updateStatus('🤖 Real AI Processing Ready - Upload an audio file to transcribe and organize your training report.');
        } else {
            this.updateStatus('⚠️ Backend not configured - Demo mode only.');
        }
        
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
            // Reset the manual abort flag for new processing
            this.wasManuallyAborted = false;
            
            // Check if this is GitHub Pages demo
            if (this.isDemoOnly) {
                this.showGitHubPagesDemo(file);
                return;
            }
            
            this.isProcessing = true;
            this.updateUploadButton('Kill Robot', false, true);
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
            // Only reset state if this wasn't a manual abort (which already handles state reset)
            if (!this.wasManuallyAborted) {
                this.isProcessing = false;
                this.updateUploadButton('Choose Audio File', false);
            }
        }
    }
    
    async showGitHubPagesDemo(file) {
        this.isProcessing = true;
        this.updateUploadButton('Kill Robot', false, true);
        this.hideError();
        this.resetProgress();
        
        // Simulate the full process for demo
        this.updateStatus(`📁 Demo: Processing ${file.name}...`);
        
        // Step 1: Upload
        this.setStepActive('upload');
        this.updateProgress(25);
        this.updateStatus('📤 Demo: Uploading audio file...');
        await this.simulateDelay(800);
        
        // Step 2: Transcribe
        this.setStepActive('transcribe');
        this.updateProgress(50);
        this.updateStatus('🎤 Demo: Transcribing audio with AI... (This is a simulation)');
        await this.simulateDelay(2000);
        
        // Step 3: Analyze
        this.setStepActive('analyze');
        this.updateProgress(75);
        this.updateStatus('🧠 Demo: Analyzing content and organizing... (This is a simulation)');
        await this.simulateDelay(1500);
        
        // Step 4: Complete
        this.setStepActive('complete');
        this.updateProgress(100);
        this.updateStatus('✅ Demo: Filling form fields with sample data...');
        
        // Inject demo data
        this.injectDemoData();
        
        this.updateStatus('🌟 Demo complete! This shows how the AI would populate the form. For real functionality, deploy the backend or run locally.');
        this.isProcessing = false;
        this.updateUploadButton('Choose Audio File', false);
    }
    
    injectDemoData() {
        const demoData = {
            postost_wins: "1. Preston Location: Increased baseline since 2023; 30 → 32. +20% since starting.\n2. Raleigh Location: New front desk team members including Rachel (former HR manager) who did great in role-playing and engaging.\n3. Successful Invisalign open house with 21/21 patients arriving and starting treatment in a single day.",
            
            client_goals: "1. Preston: NP Baseline 32; NP Goal 35. No referral goal currently set.\n2. Incentives are in place across both locations.\n3. Dr. Kashyap gives an extra $100 incentive when team members first certify (only at the Raleigh location).",
            
            postost_holdbacks: "1. Craig, their office manager, was not as engaged as hoped. He alternated between Doug's PP training and this 5-Star training.\n2. We did not get commitments from Craig at the end of the day because he was not present for the wrap-up session.\n3. Trainer doesn't feel good about the implementation due to lack of management engagement.",
            
            human_capital: "1. Set - they have enough team members to handle current capacity.\n2. Preston: Two new team members: Yessica and Tiffany; Tiffany was performing better.\n3. Raleigh: Expanded from only Trisha to include Rachael, Trisha, and Latoya.",
            
            marketing: "1. Paola manages their marketing operations.\n2. They recently had a stellar Invisalign open-house with a special promotion.\n3. 21/21 patients arrived and started treatment in a single day - majorly impressive result.",
            
            space_and_equipment: "1. Raleigh: 5 Ops; not enough space and not renovated; looking to purchase building.\n2. Preston: 7 ops; enough space; scheduling within 1 week turnaround time."
        };
        
        this.injectReportData(demoData);
    }
    
    async uploadAndProcess(file) {
        this.abortController = new AbortController();
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Track upload progress and timing
        const fileSize = file.size;
        const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(1);
        let uploadStartTime = Date.now();
        let totalStartTime = Date.now();
        
        try {
            // Step 1: Starting upload
            this.setStepActive('upload');
            this.updateProgress(5);
            this.updateStatus(`📤 Starting upload of ${file.name} (${fileSizeMB} MB)...`);
            await this.simulateDelay(500);
            
            // Step 2: Simulate upload progress
            const uploadDuration = Math.max(3, Math.min(8, Math.ceil(fileSize / (1024 * 1024) * 1.5))); // 1.5 seconds per MB
            console.log(`File size: ${fileSizeMB} MB, Upload duration: ${uploadDuration}s`);
            await this.simulateUploadProgress(fileSizeMB, uploadDuration);
            
            // Step 3: Upload completed, now waiting for server processing
            this.updateProgress(25);
            this.updateStatus(`📤 Upload complete! Server is processing ${fileSizeMB} MB... (this may take 30-90 seconds)`);
            
            // Start the actual upload (this is what takes the real time)
            const uploadPromise = fetch(`${this.apiBaseUrl}/api/post-report/audio`, {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            });
            
            // Step 4: Show server processing feedback while waiting
            this.setStepActive('transcribe');
            let waitingTime = 0;
            const maxWaitTime = 120; // 2 minutes max
            let analyzeStepActivated = false;
            
            // Show processing feedback every 3 seconds
            this.processingInterval = setInterval(() => {
                waitingTime += 3;
                const remainingEstimate = Math.max(5, 90 - waitingTime); // Estimate decreases over time
                let progressValue;
                
                if (waitingTime < 30) {
                    progressValue = 25 + (waitingTime / 60) * 35; // Progress from 25% to 60% over 60 seconds
                    this.updateStatus(`🎤 Server processing audio (${waitingTime}s elapsed, ~${remainingEstimate}s remaining)...`);
                } else if (waitingTime < 60) {
                    progressValue = 35 + ((waitingTime - 30) / 30) * 25; // Progress from 35% to 60%
                    this.updateStatus(`🎤 AI transcribing with OpenAI Whisper (${waitingTime}s elapsed, ~${remainingEstimate}s remaining)...`);
                } else if (waitingTime < 120) {
                    // Activate analyze step when we start AI analysis
                    if (!analyzeStepActivated) {
                        this.setStepActive('analyze');
                        analyzeStepActivated = true;
                    }
                    // Cap the progress calculation to prevent going over 95%
                    const analysisProgress = Math.min((waitingTime - 60) / 60, 1); // 0 to 1 over 60 seconds
                    progressValue = 60 + (analysisProgress * 35); // Progress from 60% to 95% over 60 seconds
                    this.updateStatus(`🧠 AI analyzing content with GPT-4 (${waitingTime}s elapsed, ~${Math.max(5, 120 - waitingTime)}s remaining)...`);
                } else {
                    // After 2 minutes, cap at 95% and show extended processing message
                    if (!analyzeStepActivated) {
                        this.setStepActive('analyze');
                        analyzeStepActivated = true;
                    }
                    progressValue = 95;
                    this.updateStatus(`🧠 AI processing taking longer than expected (${waitingTime}s elapsed)... Please wait.`);
                }
                
                // Always cap progress at 95% to never exceed 100% before completion
                this.updateProgress(Math.min(progressValue, 95));
            }, 3000);
            
            // Wait for the actual response
            const response = await uploadPromise;
            
            // Clean up the interval once we get a response (success or failure)
            if (this.processingInterval) {
                clearInterval(this.processingInterval);
                this.processingInterval = null;
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Get the result
            const result = await response.json();
            
            // Step 5: Complete
            this.setStepActive('complete');
            this.updateProgress(100);
            this.updateStatus('✅ AI processing complete! Filling form fields...');
            
            // Inject the data into form fields
            this.injectReportData(result.report_data);
            
            const totalTime = Math.ceil((Date.now() - totalStartTime) / 1000);
            this.updateStatus(`🎉 Success! Processed ${fileSizeMB} MB in ${totalTime}s. Form fields updated. ${result.mode === 'demo' ? '(Demo Mode)' : '(Real AI Processing)'}`);
            
        } catch (error) {
            // Clean up the interval if an error occurs
            if (this.processingInterval) {
                clearInterval(this.processingInterval);
                this.processingInterval = null;
            }
            
            if (error.name === 'AbortError' || error.message.includes('cancelled')) {
                // Only update status if this wasn't a manual abort (which already shows robot revenge message)
                if (!this.wasManuallyAborted) {
                    this.updateStatus(this.getRandomRobotRevengeMessage());
                }
            } else {
                // Check if it's a network timeout or server error
                if (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('timeout')) {
                    // For network issues, try falling back to demo mode
                    this.updateStatus('⚠️ Network issue detected. Falling back to demo mode...');
                    await this.simulateDelay(1000);
                    await this.showGitHubPagesDemo(file);
                } else {
                    // For other errors, re-throw so they get handled by the main error handler
                    throw error;
                }
            }
        }
    }
    
    async simulateUploadProgress(fileSizeMB, durationSeconds) {
        const steps = Math.max(8, Math.min(25, Math.ceil(durationSeconds * 3))); // More frequent updates
        const timePerStep = (durationSeconds * 1000) / steps;
        const progressPerStep = 15 / steps; // Upload goes from 5% to 20%
        
        console.log(`Upload simulation: ${steps} steps, ${timePerStep}ms per step`);
        
        for (let i = 0; i < steps; i++) {
            const currentProgress = 5 + (i * progressPerStep);
            const uploadedMB = ((i + 1) / steps * parseFloat(fileSizeMB)).toFixed(1);
            const remainingTime = Math.ceil((steps - i - 1) * timePerStep / 1000);
            
            this.updateProgress(currentProgress);
            
            if (remainingTime > 0) {
                this.updateStatus(`📤 Uploading ${uploadedMB}/${fileSizeMB} MB... (${remainingTime}s remaining)`);
                console.log(`Progress: ${currentProgress.toFixed(1)}% - ${uploadedMB}/${fileSizeMB} MB (${remainingTime}s remaining)`);
            } else {
                this.updateStatus(`📤 Uploading ${uploadedMB}/${fileSizeMB} MB... (finishing up)`);
                console.log(`Progress: ${currentProgress.toFixed(1)}% - ${uploadedMB}/${fileSizeMB} MB (finishing up)`);
            }
            
            await this.simulateDelay(timePerStep);
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
        // Define the step order for progression tracking
        const stepOrder = ['upload', 'transcribe', 'analyze', 'complete'];
        const currentStepIndex = stepOrder.indexOf(stepName);
        
        // Reset all steps first
        Object.keys(this.progressSteps).forEach(key => {
            const step = this.progressSteps[key];
            if (step) {
                step.classList.remove('active', 'completed');
            }
        });
        
        // Mark completed steps (all steps before current)
        for (let i = 0; i < currentStepIndex; i++) {
            const stepKey = stepOrder[i];
            const step = this.progressSteps[stepKey];
            if (step) {
                step.classList.add('completed');
            }
        }
        
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
        // Ensure progress never exceeds 100%
        const clampedPercentage = Math.min(Math.max(percentage, 0), 100);
        
        if (this.progressBar) {
            this.progressBar.style.width = `${clampedPercentage}%`;
        }
        if (this.progressPercentage) {
            this.progressPercentage.textContent = `${Math.round(clampedPercentage)}%`;
        }
    }
    
    updateStatus(message) {
        if (this.statusEl) {
            this.statusEl.textContent = message;
        }
    }
    
    updateUploadButton(text, disabled, isKillMode = false) {
        if (this.uploadBtn) {
            if (isKillMode) {
                // Kill Robot mode - red button with dead robot icon
                this.uploadBtn.innerHTML = `<i class="fas fa-robot" style="color: #ff6b6b;"></i> ${text}`;
                this.uploadBtn.style.backgroundColor = '#dc3545';
                this.uploadBtn.style.borderColor = '#dc3545';
                this.uploadBtn.style.color = 'white';
                this.uploadBtn.classList.add('btn-danger');
                this.uploadBtn.classList.remove('btn-primary');
            } else {
                // Normal mode - restore original styling
                this.uploadBtn.innerHTML = `<i class="fas fa-microphone"></i> ${text}`;
                this.uploadBtn.style.backgroundColor = '';
                this.uploadBtn.style.borderColor = '';
                this.uploadBtn.style.color = '';
                this.uploadBtn.classList.remove('btn-danger');
                this.uploadBtn.classList.add('btn-primary');
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
    
    getRandomRobotRevengeMessage() {
        const randomIndex = Math.floor(Math.random() * this.robotRevengeMessages.length);
        return this.robotRevengeMessages[randomIndex];
    }
    
    abortProcessing() {
        this.wasManuallyAborted = true; // Flag that this was a manual abort
        
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
        
        // Clean up the processing interval
        if (this.processingInterval) {
            clearInterval(this.processingInterval);
            this.processingInterval = null;
        }
        
        this.isProcessing = false;
        this.updateUploadButton('Choose Audio File', false);
        this.updateStatus(this.getRandomRobotRevengeMessage());
        this.resetProgress();
        
        // Clear the file input so user can select a new file
        if (this.fileInput) {
            this.fileInput.value = '';
        }
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
