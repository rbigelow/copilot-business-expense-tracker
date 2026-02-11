// Global variables
let currentPeriod = '30days';
let categoryChart = null;
let timeChart = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default
    document.getElementById('date').valueAsDate = new Date();
    
    // Load expenses
    loadExpenses();
    
    // Setup form handler
    document.getElementById('addExpenseForm').addEventListener('submit', handleAddExpense);
    
    // Setup period buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentPeriod = this.dataset.period;
            loadReportData();
        });
    });
});

// Section navigation
function showSection(section, event) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`${section}-section`).classList.add('active');
    event.currentTarget.classList.add('active');
    
    if (section === 'reports') {
        loadReportData();
    }
}

// Handle add expense form submission
async function handleAddExpense(e) {
    e.preventDefault();
    
    const formData = {
        date: document.getElementById('date').value,
        category: document.getElementById('category').value,
        description: document.getElementById('description').value,
        amount: document.getElementById('amount').value
    };
    
    try {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            // Reset form
            e.target.reset();
            document.getElementById('date').valueAsDate = new Date();
            
            // Reload expenses
            loadExpenses();
            
            alert('Expense added successfully!');
        } else {
            alert('Error adding expense');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding expense');
    }
}

// Load expenses
async function loadExpenses() {
    try {
        const response = await fetch('/api/expenses');
        const expenses = await response.json();
        
        const expensesList = document.getElementById('expensesList');
        
        if (expenses.length === 0) {
            expensesList.innerHTML = '<div class="empty-state"><p>No expenses recorded yet. Add your first expense above!</p></div>';
            return;
        }
        
        expensesList.innerHTML = expenses.map(expense => `
            <div class="expense-item">
                <div class="expense-details">
                    <div class="expense-date">${expense.date}</div>
                    <span class="expense-category">${expense.category}</span>
                    <div class="expense-description">${expense.description}</div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div class="expense-amount">$${parseFloat(expense.amount).toFixed(2)}</div>
                    <button class="btn btn-delete" onclick="deleteExpense(${expense.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading expenses:', error);
    }
}

// Delete expense
async function deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/expenses/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadExpenses();
            alert('Expense deleted successfully!');
        } else {
            alert('Error deleting expense');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting expense');
    }
}

// Load report data
async function loadReportData() {
    try {
        const response = await fetch(`/api/report-data/${currentPeriod}`);
        const data = await response.json();
        
        // Update summary
        document.getElementById('totalExpenses').textContent = `$${data.total.toFixed(2)}`;
        document.getElementById('totalTransactions').textContent = data.count;
        
        // Update category chart
        updateCategoryChart(data.categoryData);
        
        // Update time chart
        updateTimeChart(data.dateData);
    } catch (error) {
        console.error('Error loading report data:', error);
    }
}

// Update category chart
function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    if (data.labels.length === 0) {
        ctx.parentElement.innerHTML = '<div class="empty-state"><p>No data available for this period</p></div>';
        return;
    }
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b',
                    '#fa709a',
                    '#fee140',
                    '#30cfd0'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: $${value.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

// Update time chart
function updateTimeChart(data) {
    const ctx = document.getElementById('timeChart');
    
    if (timeChart) {
        timeChart.destroy();
    }
    
    if (data.labels.length === 0) {
        ctx.parentElement.innerHTML = '<div class="empty-state"><p>No data available for this period</p></div>';
        return;
    }
    
    timeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Daily Expenses',
                data: data.values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Export to Excel
function exportExcel() {
    window.location.href = `/export/excel/${currentPeriod}`;
}

// Export to PDF
function exportPDF() {
    window.location.href = `/export/pdf/${currentPeriod}`;
}
