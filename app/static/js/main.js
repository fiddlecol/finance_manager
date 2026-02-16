// Main JavaScript functionality

console.log('Contribution Platform loaded');

// Dark Mode Toggle
function toggleDarkMode() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    updateDarkModeButton(isDarkMode);
}

function updateDarkModeButton(isDarkMode) {
    const icon = document.getElementById('themeIcon');
    const label = document.getElementById('themeLabel');
    
    if (isDarkMode) {
        icon.textContent = '☀️';
        label.textContent = 'Light';
    } else {
        icon.textContent = '🌙';
        label.textContent = 'Dark';
    }
}

// Initialize dark mode from localStorage
function initializeDarkMode() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
        updateDarkModeButton(true);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', initializeDarkMode);

// Utility: Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 0
    }).format(amount);
}

// Utility: Auto-close alerts
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});

// Phone number validation for M-Pesa
function validatePhoneNumber(phone) {
    const kenyanPhoneRegex = /^254[0-9]{9}$/;
    return kenyanPhoneRegex.test(phone);
}

// Format phone number input
function formatPhoneInput(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (!value.startsWith('254') && value.startsWith('0')) {
        value = '254' + value.substring(1);
    } else if (!value.startsWith('254')) {
        if (value.length > 0 && !value.startsWith('254')) {
            value = '254' + value;
        }
    }
    
    return value;
}

// Refresh event progress
async function refreshEventProgress(eventId) {
    try {
        const response = await fetch(`/api/event/${eventId}`);
        const event = await response.json();
        
        if (document.getElementById('currentAmount')) {
            document.getElementById('currentAmount').textContent = formatCurrency(event.current_amount);
            
            const progressFill = document.querySelector('.progress-fill');
            if (progressFill) {
                const percent = (event.current_amount / event.target_amount * 100);
                progressFill.style.width = percent + '%';
            }
        }
    } catch (error) {
        console.error('Error refreshing progress:', error);
    }
}

// Poll for payment updates (simple implementation)
function pollPaymentStatus(checkoutRequestId, maxAttempts = 30) {
    let attempts = 0;
    
    const interval = setInterval(() => {
        attempts++;
        
        if (attempts >= maxAttempts) {
            clearInterval(interval);
            console.log('Payment polling timeout');
            return;
        }
        
        // The page will auto-refresh on callback
    }, 2000);
}

// Load expenditure summary for event
async function loadExpenditureSummary(eventId) {
    const summaryDiv = document.getElementById('expenditure-summary');
    if (!summaryDiv) return;
    
    try {
        const response = await fetch(`/api/event/${eventId}/expenditure/summary`);
        const data = await response.json();
        
        let html = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <div class="stat-card">
                    <strong>Raised</strong>
                    <div style="color: var(--success); font-size: 1.25rem; margin-top: 0.5rem;">
                        KES ${formatNumber(data.total_raised)}
                    </div>
                </div>
                <div class="stat-card">
                    <strong>Spent</strong>
                    <div style="color: var(--danger); font-size: 1.25rem; margin-top: 0.5rem;">
                        KES ${formatNumber(data.total_expenditure)}
                    </div>
                </div>
                <div class="stat-card">
                    <strong>Remaining</strong>
                    <div style="color: var(--primary); font-size: 1.25rem; margin-top: 0.5rem;">
                        KES ${formatNumber(data.remaining)}
                    </div>
                </div>
            </div>
        `;
        
        if (data.count > 0) {
            html += '<h4>Expenditure by Category:</h4>';
            html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem;">';
            
            for (const [category, amount] of Object.entries(data.by_category)) {
                const percentage = ((amount / data.total_raised) * 100).toFixed(1);
                html += `
                    <div style="background: var(--light); padding: 0.75rem; border-radius: 6px; text-align: center;">
                        <small>${category}</small>
                        <strong style="display: block; margin-top: 0.5rem;">KES ${formatNumber(amount)}</strong>
                        <small style="color: var(--secondary);">${percentage}%</small>
                    </div>
                `;
            }
            
            html += '</div>';
        } else {
            html += '<p style="color: var(--secondary);">No expenditure recorded yet</p>';
        }
        
        summaryDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading expenditure summary:', error);
        summaryDiv.innerHTML = '<p style="color: var(--secondary);">Unable to load expenditure data</p>';
    }
}

// Utility: Format number with commas
function formatNumber(num) {
    return num.toLocaleString('en-KE', {minimumFractionDigits: 0, maximumFractionDigits: 0});
}
