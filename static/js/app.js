/**
 * Research Paper Generator - Modern JavaScript
 * Clean, professional client-side functionality
 */

class ResearchPaperGenerator {
    constructor() {
        this.currentAnalysis = null;
        this.selectedTemplate = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTemplates();
    }

    bindEvents() {
        // Form submission
        document.getElementById('repoUrl')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeRepository();
            }
        });

        // Template selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.template-card')) {
                const templateId = e.target.closest('.template-card').onclick?.toString().match(/'([^']+)'/)?.[1];
                if (templateId) {
                    this.selectTemplate(templateId);
                }
            }
        });
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            const templates = await response.json();
            this.renderTemplates(templates);
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showError('Failed to load templates');
        }
    }

    renderTemplates(templates) {
        const container = document.getElementById('templateSelection');
        if (!container) return;

        container.innerHTML = '';
        
        // Group templates by publisher
        const groupedTemplates = {};
        Object.entries(templates).forEach(([id, template]) => {
            const publisher = template.name.split(' ')[0]; // IEEE, ACM, Springer, etc.
            if (!groupedTemplates[publisher]) {
                groupedTemplates[publisher] = [];
            }
            groupedTemplates[publisher].push({id, template});
        });

        // Render grouped templates
        Object.entries(groupedTemplates).forEach(([publisher, templateList]) => {
            // Add publisher header
            const headerCol = document.createElement('div');
            headerCol.className = 'col-12 mb-3';
            headerCol.innerHTML = `
                <h6 class="text-primary fw-bold mb-2">
                    <i class="fas fa-building me-2"></i>${publisher}
                </h6>
            `;
            container.appendChild(headerCol);

            // Add templates for this publisher
            templateList.forEach(({id, template}) => {
                const col = document.createElement('div');
                col.className = 'col-md-6 mb-3';
                col.innerHTML = `
                    <div class="template-card card h-100" data-template-id="${id}" onclick="app.selectTemplate('${id}', this)">
                        <div class="card-body text-center">
                            <i class="fas fa-file-alt fa-2x text-primary mb-3"></i>
                            <h6 class="card-title">${template.name}</h6>
                            <p class="card-text small text-muted">${template.description}</p>
                            <div class="small text-muted">
                                <strong>Format:</strong> ${template.format.toUpperCase()}
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(col);
            });
        });
    }

    selectTemplate(templateId, el) {
        // Remove previous selection
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection to clicked card
        const selectedCard = el || document.querySelector(`.template-card[data-template-id="${templateId}"]`);
        selectedCard.classList.add('selected');
        this.selectedTemplate = templateId;
        
        // Add visual feedback
        selectedCard.style.transform = 'scale(1.02)';
        setTimeout(() => {
            selectedCard.style.transform = '';
        }, 200);
    }

    async analyzeRepository() {
        const repoUrl = document.getElementById('repoUrl')?.value?.trim();
        const pageCount = document.getElementById('pageCount')?.value || 6;
        
        if (!repoUrl) {
            this.showError('Please enter a GitHub repository URL');
            return;
        }
        
        if (!this.selectedTemplate) {
            this.showError('Please select a journal template');
            return;
        }

        if (!this.isValidGitHubUrl(repoUrl)) {
            this.showError('Please enter a valid GitHub repository URL');
            return;
        }

        this.showLoading();
        this.updateStep(2, 'active');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    repo_url: repoUrl,
                    template: this.selectedTemplate,
                    page_count: parseInt(pageCount)
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentAnalysis = data.analysis;
                this.showAnalysisResults(data.analysis);
                this.updateStep(2, 'completed');
                this.updateStep(3, 'active');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
            this.resetForm();
        }
    }

    async generatePaper() {
        if (!this.currentAnalysis) {
            this.showError('No analysis data available');
            return;
        }

        const pageCount = parseInt(document.getElementById('pageCount')?.value || 6);
        const authorCount = parseInt(document.getElementById('authorCount')?.value || 1);
        
        // Collect author information
        const authors = [];
        for (let i = 0; i < authorCount; i++) {
            const name = document.getElementById(`authorName${i}`)?.value;
            const email = document.getElementById(`authorEmail${i}`)?.value;
            const affiliation = document.getElementById(`authorAffiliation${i}`)?.value;
            
            if (!name || !email) {
                this.showError(`Please fill in all required fields for Author ${i + 1}`);
                return;
            }
            
            authors.push({
                name: name,
                email: email,
                affiliation: affiliation || 'Not specified'
            });
        }
        
        this.showLoading('Generating your research paper component-by-component...', 'This may take a few moments');
        this.updateStep(3, 'active');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    repo_url: this.currentAnalysis.repo_url,
                    template: this.selectedTemplate,
                    page_count: pageCount,
                    authors: authors
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showPreviewSection(data.filename, data.latex_content, data.preview_url);
                this.updateStep(3, 'completed');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Generation error:', error);
            this.showError(`Paper generation failed: ${error.message}`);
            this.resetForm();
        }
    }

    showAnalysisResults(analysis) {
        this.hideLoading();
        this.showElement('analysisResult');

        // Populate analysis data
        this.setElementText('projectName', analysis.repo_name);
        this.setElementText('projectType', analysis.project_type);
        this.setElementText('fileCount', analysis.file_count);
        this.setElementText('lineCount', analysis.line_count);

        // Show technologies
        const techContainer = document.getElementById('technologies');
        if (techContainer) {
            techContainer.innerHTML = analysis.technologies.map(tech => 
                `<span class="badge bg-primary me-1 mb-1">${tech}</span>`
            ).join('');
        }

        // Add fade-in animation
        document.getElementById('analysisResult')?.classList.add('fade-in');
    }

    showPreviewSection(filename, latexContent, previewUrl) {
        this.hideLoading();
        this.showElement('previewSection');

        // Create preview section if it doesn't exist
        let previewSection = document.getElementById('previewSection');
        if (!previewSection) {
            previewSection = document.createElement('div');
            previewSection.id = 'previewSection';
            previewSection.className = 'analysis-result';
            previewSection.innerHTML = `
                <div class="alert alert-success border-0">
                    <h5 class="mb-2">
                        <i class="fas fa-file-alt me-2"></i>Paper Generated Successfully!
                    </h5>
                    <p class="mb-3">Your research paper has been generated and is ready for preview and editing.</p>
                    <div class="d-flex gap-3">
                        <a href="${previewUrl}" class="btn btn-primary btn-lg" target="_blank">
                            <i class="fas fa-eye me-2"></i>Preview & Edit
                        </a>
                        <button class="btn btn-success btn-lg" onclick="downloadLatex('${filename}')">
                            <i class="fas fa-download me-2"></i>Download LaTeX
                        </button>
                    </div>
                </div>
            `;
            
            // Insert after analysis result
            const analysisResult = document.getElementById('analysisResult');
            if (analysisResult) {
                analysisResult.parentNode.insertBefore(previewSection, analysisResult.nextSibling);
            }
        }

        // Add fade-in animation
        previewSection.classList.add('fade-in');
    }

    showDownloadSection(filename, downloadUrl) {
        this.hideLoading();
        this.showElement('downloadSection');

        const downloadLink = document.getElementById('downloadLink');
        if (downloadLink) {
            downloadLink.href = downloadUrl;
            downloadLink.download = filename;
        }

        // Add fade-in animation
        document.getElementById('downloadSection')?.classList.add('fade-in');
    }

    showLoading(title = 'Analyzing your repository...', subtitle = 'This may take a few moments') {
        this.hideElement('repository-step');
        this.hideElement('analysisResult');
        this.hideElement('downloadSection');
        this.showElement('loading');

        const loadingTitle = document.querySelector('#loading h5');
        const loadingSubtitle = document.querySelector('#loading p');
        
        if (loadingTitle) loadingTitle.textContent = title;
        if (loadingSubtitle) loadingSubtitle.textContent = subtitle;
    }

    hideLoading() {
        this.hideElement('loading');
    }

    showElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
        }
    }

    hideElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    }

    setElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
        }
    }

    updateStep(stepNumber, status) {
        const step = document.getElementById(`step${stepNumber}`);
        if (step) {
            step.className = `step ${status}`;
        }
    }

    resetForm() {
        this.hideLoading();
        this.showElement('repository-step');
        this.hideElement('analysisResult');
        this.hideElement('downloadSection');
        
        // Reset steps
        this.updateStep(1, 'active');
        this.updateStep(2, '');
        this.updateStep(3, '');
        
        // Clear form
        const repoInput = document.getElementById('repoUrl');
        if (repoInput) repoInput.value = '';
        
        // Clear template selection
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });
        this.selectedTemplate = null;
        this.currentAnalysis = null;
    }

    showError(message) {
        // Create or update error alert
        let errorAlert = document.getElementById('errorAlert');
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.id = 'errorAlert';
            errorAlert.className = 'alert alert-danger border-0 mb-4';
            errorAlert.innerHTML = `
                <h6 class="mb-2">
                    <i class="fas fa-exclamation-triangle me-2"></i>Error
                </h6>
                <p class="mb-0" id="errorMessage"></p>
            `;
            
            const form = document.querySelector('.card-body');
            if (form) {
                form.insertBefore(errorAlert, form.firstChild);
            }
        }
        
        document.getElementById('errorMessage').textContent = message;
        errorAlert.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 5000);
    }

    isValidGitHubUrl(url) {
        const githubRegex = /^https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/;
        return githubRegex.test(url);
    }
}

// Global functions for template onclick handlers
function selectTemplate(templateId) {
    app.selectTemplate(templateId);
}

function analyzeRepository() {
    app.analyzeRepository();
}

function generatePaper() {
    app.generatePaper();
}

function downloadLatex(filename) {
    const link = document.createElement('a');
    link.href = `/api/download/${filename}`;
    link.download = filename;
    link.click();
}

// Removed scroll function - no longer needed

function updateAuthorFields() {
    const count = parseInt(document.getElementById('authorCount')?.value || 1);
    const container = document.getElementById('authorsContainer');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 0; i < count; i++) {
        const authorDiv = document.createElement('div');
        authorDiv.className = 'card mb-3';
        authorDiv.innerHTML = `
            <div class="card-body">
                <h6 class="card-title">Author ${i + 1}</h6>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <input type="text" class="form-control" id="authorName${i}" 
                               placeholder="Full Name" required>
                    </div>
                    <div class="col-md-6 mb-2">
                        <input type="email" class="form-control" id="authorEmail${i}" 
                               placeholder="Email Address" required>
                    </div>
                    <div class="col-12 mb-2">
                        <input type="text" class="form-control" id="authorAffiliation${i}" 
                               placeholder="Affiliation (University/Institution)">
                    </div>
                </div>
            </div>
        `;
        container.appendChild(authorDiv);
    }
}

// Initialize with one author field on page load
document.addEventListener('DOMContentLoaded', function() {
    updateAuthorFields();
});

// Removed scroll function - no longer needed

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new ResearchPaperGenerator();
});

// Smooth scrolling for navigation links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// Add loading states to buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('button[onclick*="analyzeRepository"]')) {
        e.target.disabled = true;
        e.target.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        setTimeout(() => {
            e.target.disabled = false;
            e.target.innerHTML = '<i class="fas fa-search me-2"></i>Analyze Repository';
        }, 10000);
    }
    
    if (e.target.matches('button[onclick*="generatePaper"]')) {
        e.target.disabled = true;
        e.target.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
        setTimeout(() => {
            e.target.disabled = false;
            e.target.innerHTML = '<i class="fas fa-file-alt me-2"></i>Generate Research Paper';
        }, 15000);
    }
});
