const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const modeToggle = document.getElementById('modeToggle');
const suggestionBtns = document.querySelectorAll('.suggestion-btn');
const electionType = document.getElementById('electionType');
const stateSelect = document.getElementById('stateSelect');
const analyzeBtn = document.getElementById('analyzeBtn');

// Maintain conversation history
let conversationHistory = [];
let turnoutChartObj;
let demographicsChartObj;

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content glass-bubble';
    
    if (isUser) {
        contentDiv.textContent = content;
    } else {
        // Parse markdown for AI responses
        contentDiv.innerHTML = marked.parse(content);
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot';
        typingDiv.appendChild(dot);
    }
    
    chatContainer.appendChild(typingDiv);
    scrollToBottom();
}

function hideTyping() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function sendMessage(message) {
    if (!message.trim()) return;
    
    addMessage(message, true);
    userInput.value = '';
    sendBtn.disabled = true;
    
    const isDeepDive = modeToggle.checked;
    
    conversationHistory.push({ role: "user", parts: [{ text: message }] });
    
    showTyping();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                mode: isDeepDive ? 'deep' : 'simple',
                history: conversationHistory.slice(0, -1) // send previous history
            })
        });
        
        const data = await response.json();
        
        hideTyping();
        
        if (data.error) {
            addMessage('System Error: ' + data.error, false);
        } else {
            addMessage(data.response, false);
            conversationHistory.push({ role: "model", parts: [{ text: data.response }] });
        }
    } catch (error) {
        hideTyping();
        addMessage('System offline or connection lost.', false);
        console.error('Error:', error);
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

suggestionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        sendMessage(btn.textContent);
    });
});

electionType.addEventListener('change', () => {
    if (electionType.value === 'state') {
        stateSelect.classList.remove('hidden');
    } else {
        stateSelect.classList.add('hidden');
    }
});

analyzeBtn.addEventListener('click', async () => {
    const type = electionType.value;
    const state = stateSelect.value;
    
    if (type === 'state' && !state) {
        addMessage('Please select a state to analyze.', false);
        return;
    }
    
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '...';
    
    try {
        const response = await fetch('/api/election-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, state })
        });
        const data = await response.json();
        
        if (data.error) {
            console.error(data.error);
            addMessage('Error fetching election data: ' + data.error, false);
            return;
        }
        
        // Update stats
        const statValues = document.querySelectorAll('.stat-card .stat-value');
        if(statValues.length >= 3) {
            statValues[0].textContent = data.nextElection || 'TBD';
            statValues[1].textContent = data.registeredVoters || 'N/A';
            statValues[2].textContent = data.turnoutGoal || 'N/A';
        }
        
        // Update charts
        if (turnoutChartObj && data.turnout) {
            turnoutChartObj.data.labels = data.turnout.labels;
            turnoutChartObj.data.datasets[0].data = data.turnout.data;
            turnoutChartObj.update();
        }
        
        if (demographicsChartObj && data.partySeats) {
            demographicsChartObj.data.labels = data.partySeats.labels;
            demographicsChartObj.data.datasets[0].data = data.partySeats.data;
            
            // Generate vibrant colors for the party segments
            const colors = [
                '#ff9933', // Default Orange
                '#00f0ff', // Default Blue
                '#00ff66', // Default Green
                '#ff003c', // Red
                '#7000ff', // Purple
                '#ffff00'  // Yellow
            ];
            
            demographicsChartObj.data.datasets[0].backgroundColor = data.partySeats.data.map((_, i) => colors[i % colors.length]);
            demographicsChartObj.update();
        }
        
        // Update timeline
        if (data.timeline) {
            const timelineList = document.querySelector('.timeline-list');
            timelineList.innerHTML = '';
            data.timeline.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="date neon-text">${item.date}</span><span class="event">${item.event}</span>`;
                timelineList.appendChild(li);
            });
        }
        
        addMessage(`Dashboard updated with ${type === 'state' ? state : 'National'} election data.`, false);
        
    } catch (err) {
        console.error(err);
        addMessage('Failed to connect to the analysis engine.', false);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze';
    }
});

// Initialize Charts
document.addEventListener('DOMContentLoaded', () => {
    Chart.defaults.color = '#8a8d9e';
    Chart.defaults.font.family = "'Outfit', sans-serif";

    // Turnout Chart
    const ctxTurnout = document.getElementById('turnoutChart').getContext('2d');
    turnoutChartObj = new Chart(ctxTurnout, {
        type: 'line',
        data: {
            labels: ['2004', '2009', '2014', '2019', '2024'],
            datasets: [{
                label: 'Voter Turnout (%)',
                data: [58.07, 58.21, 66.44, 67.40, 65.79],
                borderColor: '#00f0ff',
                backgroundColor: 'rgba(0, 240, 255, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#00f0ff',
                pointBorderColor: '#fff',
                pointRadius: 4,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 22, 0.9)',
                    titleColor: '#00f0ff',
                    bodyColor: '#e0e0e0',
                    borderColor: 'rgba(0, 240, 255, 0.2)',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    });

    // Party Seats Chart
    const ctxDemographics = document.getElementById('demographicsChart').getContext('2d');
    demographicsChartObj = new Chart(ctxDemographics, {
        type: 'doughnut',
        data: {
            labels: ['NDA', 'INDIA', 'Others'],
            datasets: [{
                data: [293, 234, 16],
                backgroundColor: [
                    '#ff9933', // NDA/BJP Orange
                    '#00f0ff', // INDIA/INC Blue
                    '#00ff66'  // Others Green
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e0e0e0',
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            }
        }
    });

    // Auto-fetch data for the present year's election on load
    analyzeBtn.click();
});
