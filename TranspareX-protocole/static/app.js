// TranspareX Frontend Application
class TranspareXApp {
    constructor() {
        this.apiBase = '/api';
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        
        console.log('App initialized with token:', this.token ? this.token.substring(0, 20) + '...' : 'No token');
        console.log('App initialized with user:', this.user);
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        this.loadDashboardStats();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('loginBtn').addEventListener('click', () => this.showModal('loginModal'));
        document.getElementById('registerBtn').addEventListener('click', () => this.showModal('registerModal'));
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        document.getElementById('testDashboardBtn').addEventListener('click', () => this.testDashboard());

        // Modal close buttons
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Form submissions
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));
        document.getElementById('createFundForm').addEventListener('submit', (e) => this.handleCreateFund(e));
        document.getElementById('createTransactionForm').addEventListener('submit', (e) => this.handleCreateTransaction(e));

        // Dashboard buttons
        document.getElementById('createFundBtn').addEventListener('click', () => this.showModal('createFundModal'));
        document.getElementById('createTransactionBtn').addEventListener('click', () => this.showModal('createTransactionModal'));
    }

    checkAuthStatus() {
        if (this.token && this.user) {
            // Check if token is expired
            if (this.isTokenExpired()) {
                this.logout();
                this.showWelcome();
                return;
            }
            this.showDashboard();
            this.loadUserData();
        } else {
            this.showWelcome();
        }
    }

    isTokenExpired() {
        if (!this.token) return true;
        
        try {
            const payload = JSON.parse(atob(this.token.split('.')[1]));
            const currentTime = Date.now() / 1000;
            // Add a 60-second grace period to account for clock skew
            const gracePeriod = 60;
            const isExpired = payload.exp < (currentTime - gracePeriod);
            
            console.log('Token expiration check:', {
                currentTime: currentTime,
                expirationTime: payload.exp,
                isExpired: isExpired,
                timeUntilExpiry: payload.exp - currentTime,
                hoursUntilExpiry: (payload.exp - currentTime) / 3600,
                gracePeriod: gracePeriod
            });
            
            return isExpired;
        } catch (e) {
            console.error('Error checking token expiration:', e);
            return true;
        }
    }

    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }

    closeModal(modal) {
        modal.style.display = 'none';
        // Clear form messages
        const messageEl = modal.querySelector('.message');
        if (messageEl) {
            messageEl.textContent = '';
            messageEl.className = 'message';
        }
    }

    showWelcome() {
        document.getElementById('welcomeSection').style.display = 'block';
        document.getElementById('dashboardSection').style.display = 'none';
        document.getElementById('loginBtn').style.display = 'inline-block';
        document.getElementById('registerBtn').style.display = 'inline-block';
        document.getElementById('logoutBtn').style.display = 'none';
        document.getElementById('testDashboardBtn').style.display = 'none';
    }

    showDashboard() {
        console.log('Showing dashboard...');
        
        // Hide welcome section
        document.getElementById('welcomeSection').style.display = 'none';
        
        // Show dashboard section
        document.getElementById('dashboardSection').style.display = 'block';
        
        // Update navigation buttons
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('registerBtn').style.display = 'none';
        document.getElementById('logoutBtn').style.display = 'inline-block';
        document.getElementById('testDashboardBtn').style.display = 'inline-block';
        
        // Check if buttons exist and are visible
        const createFundBtn = document.getElementById('createFundBtn');
        const createTransactionBtn = document.getElementById('createTransactionBtn');
        
        console.log('Dashboard buttons check:', {
            createFundBtn: createFundBtn ? 'exists' : 'missing',
            createTransactionBtn: createTransactionBtn ? 'exists' : 'missing',
            dashboardSection: document.getElementById('dashboardSection').style.display
        });
        
        // Make buttons more visible for testing
        if (createFundBtn) {
            createFundBtn.style.backgroundColor = '#28a745';
            createFundBtn.style.color = 'white';
            createFundBtn.style.padding = '15px 30px';
            createFundBtn.style.fontSize = '16px';
            createFundBtn.style.border = 'none';
            createFundBtn.style.borderRadius = '5px';
            createFundBtn.style.cursor = 'pointer';
        }
        
        if (createTransactionBtn) {
            createTransactionBtn.style.backgroundColor = '#007bff';
            createTransactionBtn.style.color = 'white';
            createTransactionBtn.style.padding = '15px 30px';
            createTransactionBtn.style.fontSize = '16px';
            createTransactionBtn.style.border = 'none';
            createTransactionBtn.style.borderRadius = '5px';
            createTransactionBtn.style.cursor = 'pointer';
        }
        
        this.loadDashboardData();
    }

    testDashboard() {
        console.log('Test dashboard clicked');
        console.log('Current token:', this.token ? this.token.substring(0, 20) + '...' : 'No token');
        console.log('Current user:', this.user);
        this.showDashboard();
    }

    async loadDashboardStats() {
        try {
            if (!this.token || this.isTokenExpired()) {
                return;
            }
            
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/dashboard/stats`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateStats(data.stats);
                }
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    updateStats(stats) {
        document.getElementById('totalFunds').textContent = stats.total_funds || 0;
        document.getElementById('totalTransactions').textContent = stats.total_transactions || 0;
        document.getElementById('completedTransactions').textContent = stats.completed_transactions || 0;
        document.getElementById('blockchainBalance').textContent = (stats.blockchain_balance || 0).toFixed(4) + ' ETH';
    }

    async loadUserData() {
        if (this.user) {
            document.getElementById('userInfo').textContent = 
                `${this.user.username} (${this.user.role})`;
        }
    }

    async loadDashboardData() {
        console.log('Loading dashboard data with token:', this.token ? this.token.substring(0, 20) + '...' : 'No token');
        await Promise.all([
            this.loadFunds(),
            this.loadTransactions(),
            this.loadBlockchainEvents()
        ]);
    }

    async loadFunds() {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/funds`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.displayFunds(data.funds);
                }
            }
        } catch (error) {
            console.error('Error loading funds:', error);
        }
    }

    displayFunds(funds) {
        const container = document.getElementById('fundsList');
        
        if (funds.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-piggy-bank"></i>
                    <h3>No Funds</h3>
                    <p>Create your first fund to get started</p>
                </div>
            `;
            return;
        }

        container.innerHTML = funds.map(fund => `
            <div class="list-item">
                <h4>${fund.name}</h4>
                <p><strong>Total:</strong> ${fund.total_amount} ETH</p>
                <p><strong>Remaining:</strong> ${fund.remaining_amount} ETH</p>
                <p><strong>Status:</strong> <span class="status-badge status-${fund.status}">${fund.status}</span></p>
                <p><strong>Created:</strong> ${new Date(fund.created_at).toLocaleDateString()}</p>
            </div>
        `).join('');
    }

    async loadTransactions() {
        try {
            const response = await fetch(`${this.apiBase}/transactions`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.displayTransactions(data.transactions);
                }
            }
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    displayTransactions(transactions) {
        const container = document.getElementById('transactionsList');
        
        if (transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exchange-alt"></i>
                    <h3>No Transactions</h3>
                    <p>Create your first transaction to get started</p>
                </div>
            `;
            return;
        }

        container.innerHTML = transactions.slice(0, 5).map(tx => `
            <div class="list-item">
                <h4>Transaction #${tx.id}</h4>
                <p><strong>Recipient:</strong> ${tx.recipient_address}</p>
                <p><strong>Amount:</strong> ${tx.amount} ETH</p>
                <p><strong>Status:</strong> <span class="status-badge status-${tx.status}">${tx.status}</span></p>
                <p><strong>Created:</strong> ${new Date(tx.created_at).toLocaleDateString()}</p>
                ${tx.transaction_hash ? `<p><strong>Hash:</strong> ${tx.transaction_hash.substring(0, 10)}...</p>` : ''}
            </div>
        `).join('');
    }

    async loadBlockchainEvents() {
        try {
            const response = await fetch(`${this.apiBase}/blockchain/events`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.displayBlockchainEvents(data.events);
                }
            }
        } catch (error) {
            console.error('Error loading blockchain events:', error);
        }
    }

    displayBlockchainEvents(events) {
        const container = document.getElementById('blockchainEvents');
        
        if (events.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-link"></i>
                    <h3>No Events</h3>
                    <p>Blockchain events will appear here</p>
                </div>
            `;
            return;
        }

        container.innerHTML = events.slice(0, 5).map(event => `
            <div class="list-item">
                <h4>Fund Released Event</h4>
                <p><strong>Recipient:</strong> ${event.recipient}</p>
                <p><strong>Amount:</strong> ${event.amount} ETH</p>
                <p><strong>Block:</strong> ${event.block_number}</p>
                <p><strong>Hash:</strong> ${event.transaction_hash.substring(0, 10)}...</p>
            </div>
        `).join('');
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const messageEl = document.getElementById('loginMessage');
        
        try {
            const response = await fetch(`${this.apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.token = data.token;
                this.user = data.user;
                localStorage.setItem('token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                
                console.log('Login successful, token stored:', this.token.substring(0, 20) + '...');
                console.log('User data:', this.user);
                
                messageEl.textContent = 'Login successful!';
                messageEl.className = 'message success';
                
                setTimeout(() => {
                    this.closeModal(document.getElementById('loginModal'));
                    this.showDashboard();
                }, 1000);
            } else {
                messageEl.textContent = data.message;
                messageEl.className = 'message error';
            }
        } catch (error) {
            messageEl.textContent = 'Login failed. Please try again.';
            messageEl.className = 'message error';
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const messageEl = document.getElementById('registerMessage');
        
        try {
            const response = await fetch(`${this.apiBase}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                messageEl.textContent = 'Registration successful! Please login.';
                messageEl.className = 'message success';
                
                setTimeout(() => {
                    this.closeModal(document.getElementById('registerModal'));
                    this.showModal('loginModal');
                }, 1000);
            } else {
                messageEl.textContent = data.message;
                messageEl.className = 'message error';
            }
        } catch (error) {
            messageEl.textContent = 'Registration failed. Please try again.';
            messageEl.className = 'message error';
        }
    }

    async handleCreateFund(e) {
        e.preventDefault();
        
        const name = document.getElementById('fundName').value;
        const description = document.getElementById('fundDescription').value;
        const total_amount = parseFloat(document.getElementById('fundAmount').value);
        const messageEl = document.getElementById('createFundMessage');
        
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/funds`, {
                method: 'POST',
                body: JSON.stringify({ name, description, total_amount })
            });
            
            const data = await response.json();
            
            if (data.success) {
                messageEl.textContent = 'Fund created successfully!';
                messageEl.className = 'message success';
                
                setTimeout(() => {
                    this.closeModal(document.getElementById('createFundModal'));
                    this.loadFunds();
                    this.loadDashboardStats();
                }, 1000);
            } else {
                messageEl.textContent = data.message;
                messageEl.className = 'message error';
            }
        } catch (error) {
            messageEl.textContent = error.message || 'Failed to create fund. Please try again.';
            messageEl.className = 'message error';
        }
    }

    async handleCreateTransaction(e) {
        e.preventDefault();
        
        const fund_id = parseInt(document.getElementById('transactionFund').value);
        const recipient_address = document.getElementById('recipientAddress').value;
        const amount = parseFloat(document.getElementById('transactionAmount').value);
        const messageEl = document.getElementById('createTransactionMessage');
        
        try {
            const response = await fetch(`${this.apiBase}/transactions`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ fund_id, recipient_address, amount })
            });
            
            const data = await response.json();
            
            if (data.success) {
                messageEl.textContent = 'Transaction created successfully!';
                messageEl.className = 'message success';
                
                setTimeout(() => {
                    this.closeModal(document.getElementById('createTransactionModal'));
                    this.loadTransactions();
                    this.loadFunds();
                    this.loadDashboardStats();
                }, 1000);
            } else {
                messageEl.textContent = data.message;
                messageEl.className = 'message error';
            }
        } catch (error) {
            messageEl.textContent = 'Failed to create transaction. Please try again.';
            messageEl.className = 'message error';
        }
    }

    async loadFundOptions() {
        try {
            const response = await fetch(`${this.apiBase}/funds`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const select = document.getElementById('transactionFund');
                    select.innerHTML = '<option value="">Select a fund</option>';
                    
                    data.funds.forEach(fund => {
                        if (fund.remaining_amount > 0) {
                            const option = document.createElement('option');
                            option.value = fund.id;
                            option.textContent = `${fund.name} (${fund.remaining_amount} ETH available)`;
                            select.appendChild(option);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error loading fund options:', error);
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.showWelcome();
    }

    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        console.log('getAuthHeaders called:', {
            hasToken: !!this.token,
            tokenPreview: this.token ? this.token.substring(0, 20) + '...' : 'No token',
            isExpired: this.token ? this.isTokenExpired() : 'No token to check'
        });
        
        if (this.token && !this.isTokenExpired()) {
            headers['Authorization'] = `Bearer ${this.token}`;
            console.log('✅ Token included in request:', this.token.substring(0, 20) + '...');
        } else {
            console.log('❌ No valid token available - Token:', !!this.token, 'Expired:', this.token ? this.isTokenExpired() : 'N/A');
        }
        
        return headers;
    }

    async makeAuthenticatedRequest(url, options = {}) {
        // Check if token is expired before making request
        if (this.isTokenExpired()) {
            this.logout();
            this.showWelcome();
            throw new Error('Token has expired. Please login again.');
        }

        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        });

        // Handle 401 Unauthorized responses
        if (response.status === 401) {
            this.logout();
            this.showWelcome();
            throw new Error('Session expired. Please login again.');
        }

        return response;
    }

    startRealTimeUpdates() {
        // Update dashboard stats every 30 seconds
        setInterval(() => {
            if (this.token) {
                this.loadDashboardStats();
                this.loadBlockchainEvents();
            }
        }, 30000);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TranspareXApp();
    
    // Load fund options when create transaction modal is opened
    document.getElementById('createTransactionBtn').addEventListener('click', () => {
        window.app.loadFundOptions();
    });
});
