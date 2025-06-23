// JavaScript para el Agente de IA Conversacional

class AIAgentApp {
    constructor() {
        this.apiBaseUrl = '';
        this.currentSection = 'chat';
        this.isLoading = false;
        this.chatHistory = [];
        this.knowledgeItems = [];
        this.systemStatus = {};
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkSystemHealth();
        this.loadKnowledgeBase();
        this.loadAnalytics();
        this.setupCharts();
        
        // Mostrar mensaje de bienvenida
        this.updateStatus('Conectado', true);
    }
    
    bindEvents() {
        // Navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });
        
        // Chat functionality
        const sendButton = document.getElementById('send-button');
        const userInput = document.getElementById('user-input');
        
        sendButton.addEventListener('click', () => this.sendMessage());
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Character counter
        userInput.addEventListener('input', (e) => {
            const count = e.target.value.length;
            document.getElementById('char-count').textContent = count;
        });
        
        // Chat controls
        document.getElementById('clear-chat').addEventListener('click', () => this.clearChat());
        document.getElementById('export-chat').addEventListener('click', () => this.exportChat());
        
        // Knowledge base
        document.getElementById('save-knowledge').addEventListener('click', () => this.saveKnowledge());
        document.getElementById('refresh-knowledge').addEventListener('click', () => this.loadKnowledgeBase());
        document.getElementById('knowledge-search').addEventListener('input', (e) => this.filterKnowledge(e.target.value));
        document.getElementById('category-filter').addEventListener('change', (e) => this.filterKnowledge(null, e.target.value));
        
        // Settings
        document.getElementById('test-connection').addEventListener('click', () => this.testConnection());
        document.getElementById('temperature-slider').addEventListener('input', (e) => {
            document.getElementById('temperature-value').textContent = e.target.value;
        });
        document.getElementById('confidence-threshold').addEventListener('input', (e) => {
            document.getElementById('confidence-value').textContent = e.target.value;
        });
    }
    
    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');
        
        // Update content
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');
        
        this.currentSection = section;
        
        // Load section-specific data
        if (section === 'analytics') {
            this.loadAnalytics();
        } else if (section === 'settings') {
            this.loadSystemStatus();
        }
    }
    
    async sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        userInput.value = '';
        document.getElementById('char-count').textContent = '0';
        
        // Show loading
        this.setLoading(true);
        
        try {
            const response = await this.callAPI('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    context: ''
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.addMessage(data.answer, 'bot', {
                    confidence: data.confidence,
                    sources: data.sources,
                    classification: data.classification
                });
            } else {
                throw new Error('Error en la respuesta del servidor');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage(
                'Lo siento, hubo un error procesando tu mensaje. Por favor, intenta nuevamente.',
                'bot',
                { confidence: 0, sources: [], classification: 'error' }
            );
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(text, sender, metadata = {}) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const time = new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        let confidenceBadge = '';
        let sourceInfo = '';
        let classificationInfo = '';
        
        if (sender === 'bot' && metadata.confidence !== undefined) {
            const confidence = Math.round(metadata.confidence * 100);
            let confidenceClass = 'confidence-low';
            if (confidence >= 70) confidenceClass = 'confidence-high';
            else if (confidence >= 40) confidenceClass = 'confidence-medium';
            
            confidenceBadge = `<span class="confidence-badge ${confidenceClass}">Confianza: ${confidence}%</span>`;
            
            if (metadata.sources && metadata.sources.length > 0) {
                sourceInfo = `<br><small>Fuentes: ${metadata.sources.join(', ')}</small>`;
            }
            
            if (metadata.classification) {
                classificationInfo = `<br><small>Categoría: ${metadata.classification}</small>`;
            }
        }
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-time">${time}</div>
                ${sender === 'bot' ? `<div class="message-info">${confidenceBadge}${sourceInfo}${classificationInfo}</div>` : ''}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.chatHistory.push({
            text,
            sender,
            timestamp: new Date(),
            metadata
        });
    }
    
    formatMessage(text) {
        // Convert line breaks to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Convert bullet points
        text = text.replace(/^• /gm, '&bull; ');
        text = text.replace(/^\* /gm, '&bull; ');
        
        // Convert numbered lists
        text = text.replace(/^(\d+)\. /gm, '$1. ');
        
        return text;
    }
    
    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar el chat?')) {
            document.getElementById('chat-messages').innerHTML = `
                <div class="message bot-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">
                            ¡Hola! Soy tu asistente de IA organizacional. ¿En qué puedo ayudarte hoy?
                        </div>
                        <div class="message-time">Ahora</div>
                    </div>
                </div>
            `;
            this.chatHistory = [];
        }
    }
    
    exportChat() {
        const chatData = this.chatHistory.map(msg => ({
            timestamp: msg.timestamp.toISOString(),
            sender: msg.sender,
            message: msg.text,
            metadata: msg.metadata
        }));
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    async loadKnowledgeBase() {
        try {
            const response = await this.callAPI('/api/knowledge');
            if (response.ok) {
                const data = await response.json();
                this.knowledgeItems = data.items;
                this.renderKnowledgeItems(this.knowledgeItems);
            }
        } catch (error) {
            console.error('Error loading knowledge base:', error);
        }
    }
    
    renderKnowledgeItems(items) {
        const grid = document.getElementById('knowledge-grid');
        
        if (items.length === 0) {
            grid.innerHTML = '<p class="text-muted">No hay elementos en la base de conocimiento.</p>';
            return;
        }
        
        grid.innerHTML = items.map(item => `
            <div class="knowledge-item">
                <h5>${item.title}</h5>
                <span class="category-badge">${item.category}</span>
                <div class="content-preview text-truncate-3">
                    ${item.content.substring(0, 200)}${item.content.length > 200 ? '...' : ''}
                </div>
                <div class="item-meta">
                    Actualizado: ${new Date(item.updated_at).toLocaleDateString('es-ES')}
                </div>
            </div>
        `).join('');
    }
    
    filterKnowledge(searchTerm = null, category = null) {
        let filtered = this.knowledgeItems;
        
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filtered = filtered.filter(item => 
                item.title.toLowerCase().includes(term) ||
                item.content.toLowerCase().includes(term)
            );
        }
        
        if (category) {
            filtered = filtered.filter(item => item.category === category);
        }
        
        this.renderKnowledgeItems(filtered);
    }
    
    async saveKnowledge() {
        const title = document.getElementById('knowledge-title').value;
        const category = document.getElementById('knowledge-category').value;
        const content = document.getElementById('knowledge-content').value;
        
        if (!title || !category || !content) {
            alert('Por favor, completa todos los campos.');
            return;
        }
        
        try {
            const response = await this.callAPI('/api/knowledge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, category, content })
            });
            
            if (response.ok) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addKnowledgeModal'));
                modal.hide();
                
                // Clear form
                document.getElementById('knowledge-form').reset();
                
                // Reload knowledge base
                this.loadKnowledgeBase();
                
                alert('Conocimiento agregado exitosamente.');
            } else {
                throw new Error('Error guardando conocimiento');
            }
        } catch (error) {
            console.error('Error saving knowledge:', error);
            alert('Error guardando conocimiento. Por favor, intenta nuevamente.');
        }
    }
    
    async loadAnalytics() {
        // Simulate analytics data
        const analytics = {
            totalQueries: this.chatHistory.length,
            successRate: 85,
            avgResponseTime: 1.2,
            avgConfidence: 78,
            categoryData: {
                'Recursos Humanos': 35,
                'Tecnología': 28,
                'Procesos': 20,
                'Políticas': 12,
                'General': 5
            },
            trendData: [10, 15, 12, 18, 22, 25, 20]
        };
        
        // Update metrics
        document.getElementById('total-queries').textContent = analytics.totalQueries;
        document.getElementById('success-rate').textContent = `${analytics.successRate}%`;
        document.getElementById('avg-response-time').textContent = `${analytics.avgResponseTime}s`;
        document.getElementById('avg-confidence').textContent = `${analytics.avgConfidence}%`;
        
        // Update charts
        this.updateCharts(analytics);
    }
    
    setupCharts() {
        // Category Chart
        const categoryCtx = document.getElementById('category-chart').getContext('2d');
        this.categoryChart = new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Trend Chart
        const trendCtx = document.getElementById('trend-chart').getContext('2d');
        this.trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                datasets: [{
                    label: 'Consultas',
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    updateCharts(analytics) {
        // Update category chart
        this.categoryChart.data.labels = Object.keys(analytics.categoryData);
        this.categoryChart.data.datasets[0].data = Object.values(analytics.categoryData);
        this.categoryChart.update();
        
        // Update trend chart
        this.trendChart.data.datasets[0].data = analytics.trendData;
        this.trendChart.update();
    }
    
    async checkSystemHealth() {
        try {
            const response = await this.callAPI('/health');
            if (response.ok) {
                const data = await response.json();
                this.systemStatus = data.services;
                this.updateStatus('Conectado', true);
                this.loadSystemStatus();
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            console.error('Health check error:', error);
            this.updateStatus('Desconectado', false);
        }
    }
    
    loadSystemStatus() {
        const statusContainer = document.getElementById('system-status');
        
        const services = [
            { name: 'GenAI', key: 'genai', label: 'Modelo de Lenguaje' },
            { name: 'Embeddings', key: 'embedding', label: 'Búsqueda Semántica' },
            { name: 'Knowledge Base', key: 'knowledge_base', label: 'Base de Conocimiento' },
            { name: 'ML Classifier', key: 'ml_classifier', label: 'Clasificador ML' }
        ];
        
        statusContainer.innerHTML = services.map(service => {
            const status = this.systemStatus[service.key] ? 'online' : 'offline';
            const statusText = status === 'online' ? 'En línea' : 'Fuera de línea';
            
            return `
                <div class="status-item">
                    <span>${service.label}</span>
                    <span class="status ${status}">${statusText}</span>
                </div>
            `;
        }).join('');
    }
    
    async testConnection() {
        this.setLoading(true);
        await this.checkSystemHealth();
        this.setLoading(false);
        
        const allOnline = Object.values(this.systemStatus).every(status => status);
        alert(allOnline ? 'Conexión exitosa. Todos los servicios están en línea.' : 'Algunos servicios no están disponibles.');
    }
    
    updateStatus(text, isConnected) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status-dot');
        
        statusText.textContent = text;
        statusDot.className = `status-dot ${isConnected ? '' : 'disconnected'}`;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = loading ? 'flex' : 'none';
        
        const sendButton = document.getElementById('send-button');
        sendButton.disabled = loading;
    }
    
    async callAPI(endpoint, options = {}) {
        const url = this.apiBaseUrl + endpoint;
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            return response;
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.aiAgent = new AIAgentApp();
});

// Handle responsive sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('show');
}

// Add mobile menu button if needed
if (window.innerWidth <= 768) {
    const header = document.querySelector('.chat-header');
    if (header) {
        const menuButton = document.createElement('button');
        menuButton.className = 'btn btn-outline-secondary btn-sm';
        menuButton.innerHTML = '<i class="fas fa-bars"></i>';
        menuButton.onclick = toggleSidebar;
        header.insertBefore(menuButton, header.firstChild);
    }
}

