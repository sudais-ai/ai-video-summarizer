document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const loginBtn = document.getElementById('loginBtn');
    const authModal = document.getElementById('authModal');
    const modalClose = document.getElementById('modalClose');
    const authTabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const videoUrlInput = document.getElementById('videoUrl');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultsSection = document.getElementById('resultsSection');
    const tabs = document.querySelectorAll('.tab');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const historyList = document.getElementById('historyList');

    let currentUser = null;
    let currentResult = null;
    let quizAnswers = {};
    let quizSubmitted = false;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.setAttribute('data-theme', 'light');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }

    themeToggle.addEventListener('click', function() {
        const currentTheme = document.body.getAttribute('data-theme');
        if (currentTheme === 'light') {
            document.body.removeAttribute('data-theme');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.setAttribute('data-theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'light');
        }
    });

    function showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    async function checkAuth() {
        try {
            const response = await fetch('/api/user');
            const data = await response.json();
            if (data.authenticated) {
                currentUser = data.user;
                updateUserUI();
                loadHistory();
            }
        } catch (error) {
            console.error('Auth check error:', error);
        }
    }

    function updateUserUI() {
        if (currentUser) {
            loginBtn.innerHTML = `<i class="fas fa-user"></i><span>${currentUser.username}</span>`;
            loginBtn.onclick = logout;
        } else {
            loginBtn.innerHTML = '<i class="fas fa-user"></i><span>Login</span>';
            loginBtn.onclick = () => authModal.classList.add('active');
        }
    }

    async function logout() {
        try {
            await fetch('/api/logout', { method: 'POST' });
            currentUser = null;
            updateUserUI();
            historyList.innerHTML = '<p class="history-empty">Login to see your history</p>';
            showToast('Logged out successfully');
        } catch (error) {
            showToast('Logout failed', 'error');
        }
    }

    loginBtn.addEventListener('click', function() {
        if (!currentUser) {
            authModal.classList.add('active');
        }
    });

    modalClose.addEventListener('click', function() {
        authModal.classList.remove('active');
    });

    authModal.addEventListener('click', function(e) {
        if (e.target === authModal) {
            authModal.classList.remove('active');
        }
    });

    authTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            authTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            if (this.dataset.auth === 'login') {
                loginForm.classList.remove('hidden');
                registerForm.classList.add('hidden');
            } else {
                loginForm.classList.add('hidden');
                registerForm.classList.remove('hidden');
            }
        });
    });

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (data.success) {
                currentUser = data.user;
                updateUserUI();
                authModal.classList.remove('active');
                loadHistory();
                showToast('Welcome back!');
            } else {
                document.getElementById('loginError').textContent = data.error;
            }
        } catch (error) {
            document.getElementById('loginError').textContent = 'Login failed. Please try again.';
        }
    });

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            if (data.success) {
                currentUser = data.user;
                updateUserUI();
                authModal.classList.remove('active');
                loadHistory();
                showToast('Account created successfully!');
            } else {
                document.getElementById('registerError').textContent = data.error;
            }
        } catch (error) {
            document.getElementById('registerError').textContent = 'Registration failed. Please try again.';
        }
    });

    analyzeBtn.addEventListener('click', analyzeVideo);
    videoUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') analyzeVideo();
    });

    async function analyzeVideo() {
        const url = videoUrlInput.value.trim();
        if (!url) {
            showToast('Please enter a video URL', 'error');
            return;
        }

        analyzeBtn.disabled = true;
        resultsSection.classList.remove('active');
        loadingOverlay.classList.add('active');

        try {
            const response = await fetch('/api/process_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            loadingOverlay.classList.remove('active');

            if (data.success) {
                currentResult = data;
                displayResults(data);
                resultsSection.classList.add('active');
                showToast('Video analyzed successfully!');
                if (currentUser) loadHistory();
            } else {
                showToast(data.error || 'Failed to analyze video', 'error');
            }
        } catch (error) {
            loadingOverlay.classList.remove('active');
            showToast('An error occurred. Please try again.', 'error');
        } finally {
            analyzeBtn.disabled = false;
        }
    }

    function displayResults(data) {
        document.getElementById('videoTitle').textContent = data.title;

        const summaryContent = document.getElementById('summaryContent');
        const summary = data.summary;
        if (typeof summary === 'object') {
            summaryContent.innerHTML = `<p>${summary.summary || 'No summary available'}</p>`;
        } else {
            summaryContent.innerHTML = `<p>${summary}</p>`;
        }

        const keypointsList = document.getElementById('keypointsList');
        keypointsList.innerHTML = '';
        const keyPoints = summary.key_points || [];
        keyPoints.forEach((point, index) => {
            keypointsList.innerHTML += `
                <div class="keypoint-item" style="animation-delay: ${index * 0.1}s">
                    <div class="keypoint-icon"><i class="fas fa-check"></i></div>
                    <div class="keypoint-text">${point}</div>
                </div>
            `;
        });

        displayQuiz(data.quiz);
    }

    function displayQuiz(quiz) {
        const quizContainer = document.getElementById('quizContainer');
        quizContainer.innerHTML = '';
        quizAnswers = {};
        quizSubmitted = false;
        document.getElementById('quizScore').classList.remove('active');

        if (!quiz || quiz.length === 0) {
            quizContainer.innerHTML = '<p>No quiz available for this video.</p>';
            return;
        }

        quiz.forEach((q, index) => {
            const questionHtml = `
                <div class="quiz-question" data-question="${index}">
                    <div class="question-number">Question ${index + 1}</div>
                    <div class="question-text">${q.question}</div>
                    <div class="options-list">
                        ${(q.options || []).map((opt, optIndex) => `
                            <div class="option-item" data-question="${index}" data-option="${String.fromCharCode(65 + optIndex)}">
                                <span class="option-letter">${String.fromCharCode(65 + optIndex)}</span>
                                <span class="option-text">${opt.replace(/^[A-D]\)\s*/, '')}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            quizContainer.innerHTML += questionHtml;
        });

        quizContainer.innerHTML += `
            <button class="action-btn" id="submitQuiz" style="width: 100%; justify-content: center; margin-top: 1rem;">
                <i class="fas fa-check"></i> Submit Answers
            </button>
        `;

        quizContainer.querySelectorAll('.option-item').forEach(option => {
            option.addEventListener('click', function() {
                if (quizSubmitted) return;
                
                const questionIndex = this.dataset.question;
                const selectedOption = this.dataset.option;
                
                this.closest('.quiz-question').querySelectorAll('.option-item').forEach(opt => {
                    opt.classList.remove('selected');
                });
                this.classList.add('selected');
                quizAnswers[questionIndex] = selectedOption;
            });
        });

        document.getElementById('submitQuiz').addEventListener('click', function() {
            if (quizSubmitted) return;
            submitQuiz(quiz);
        });
    }

    function submitQuiz(quiz) {
        quizSubmitted = true;
        let correct = 0;

        quiz.forEach((q, index) => {
            const userAnswer = quizAnswers[index];
            const correctAnswer = q.correct;
            
            const questionEl = document.querySelector(`.quiz-question[data-question="${index}"]`);
            questionEl.querySelectorAll('.option-item').forEach(opt => {
                const optionLetter = opt.dataset.option;
                if (optionLetter === correctAnswer) {
                    opt.classList.add('correct');
                } else if (optionLetter === userAnswer && userAnswer !== correctAnswer) {
                    opt.classList.add('incorrect');
                }
            });

            if (userAnswer === correctAnswer) correct++;
        });

        const scoreEl = document.getElementById('quizScore');
        scoreEl.textContent = `Your Score: ${correct} / ${quiz.length} (${Math.round(correct / quiz.length * 100)}%)`;
        scoreEl.classList.add('active');

        document.getElementById('submitQuiz').style.display = 'none';
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            const tabName = this.dataset.tab;
            document.getElementById(tabName + 'Tab').classList.add('active');
        });
    });

    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendChatMessage();
    });

    async function sendChatMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        chatMessages.innerHTML += `
            <div class="chat-message user">
                <div class="message-avatar"><i class="fas fa-user"></i></div>
                <div class="message-content"><p>${message}</p></div>
            </div>
        `;
        chatInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        chatMessages.innerHTML += `
            <div class="chat-message bot" id="typingIndicator">
                <div class="message-avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content"><p><i class="fas fa-spinner fa-spin"></i> Thinking...</p></div>
            </div>
        `;
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            document.getElementById('typingIndicator').remove();

            if (data.success) {
                chatMessages.innerHTML += `
                    <div class="chat-message bot">
                        <div class="message-avatar"><i class="fas fa-robot"></i></div>
                        <div class="message-content"><p>${data.response}</p></div>
                    </div>
                `;
            } else {
                chatMessages.innerHTML += `
                    <div class="chat-message bot">
                        <div class="message-avatar"><i class="fas fa-robot"></i></div>
                        <div class="message-content"><p>Sorry, I couldn't process that. ${data.error || 'Please try again.'}</p></div>
                    </div>
                `;
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            document.getElementById('typingIndicator')?.remove();
            chatMessages.innerHTML += `
                <div class="chat-message bot">
                    <div class="message-avatar"><i class="fas fa-robot"></i></div>
                    <div class="message-content"><p>Sorry, something went wrong. Please try again.</p></div>
                </div>
            `;
        }
    }

    downloadPdfBtn.addEventListener('click', async function() {
        if (!currentResult) {
            showToast('No results to download', 'error');
            return;
        }

        try {
            const response = await fetch('/api/download_pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: currentResult.title,
                    summary: currentResult.summary,
                    quiz: currentResult.quiz
                })
            });

            const data = await response.json();
            if (data.success) {
                const link = document.createElement('a');
                link.href = 'data:application/pdf;base64,' + data.pdf;
                link.download = data.filename;
                link.click();
                showToast('PDF downloaded successfully!');
            } else {
                showToast(data.error || 'Failed to generate PDF', 'error');
            }
        } catch (error) {
            showToast('Failed to download PDF', 'error');
        }
    });

    async function loadHistory() {
        if (!currentUser) return;

        try {
            const response = await fetch('/api/history');
            const data = await response.json();

            if (data.success && data.history.length > 0) {
                historyList.innerHTML = '';
                data.history.forEach(item => {
                    const date = new Date(item.created_at).toLocaleDateString();
                    historyList.innerHTML += `
                        <div class="history-item" data-id="${item.id}">
                            <h4>${item.title}</h4>
                            <span>${date}</span>
                        </div>
                    `;
                });

                historyList.querySelectorAll('.history-item').forEach(item => {
                    item.addEventListener('click', () => loadHistoryItem(item.dataset.id));
                });
            } else {
                historyList.innerHTML = '<p class="history-empty">No history yet</p>';
            }
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    async function loadHistoryItem(id) {
        try {
            const response = await fetch(`/api/history/${id}`);
            const data = await response.json();

            if (data.success) {
                currentResult = {
                    title: data.item.title,
                    summary: data.item.summary,
                    quiz: data.item.quiz
                };
                displayResults(currentResult);
                resultsSection.classList.add('active');
            }
        } catch (error) {
            showToast('Failed to load history item', 'error');
        }
    }

    const chatToggle = document.getElementById('chatToggle');
    const chatSidebar = document.getElementById('chatSidebar');

    chatToggle.addEventListener('click', function() {
        chatSidebar.classList.toggle('collapsed');
        chatSidebar.classList.toggle('active');
    });

    checkAuth();
});
