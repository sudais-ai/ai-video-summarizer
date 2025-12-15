document.addEventListener('DOMContentLoaded', function() {
    const videoInput = document.getElementById('videoUrl');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const summaryContent = document.getElementById('summaryContent');
    const keyPointsContent = document.getElementById('keyPointsContent');
    const quizContent = document.getElementById('quizContent');
    const videoMeta = document.getElementById('videoMeta');
    const inputSection = document.querySelector('.input-section');
    
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatMessages = document.getElementById('chatbotMessages');

    let currentData = {
        title: '',
        summary: null,
        quiz: []
    };

    let userAnswers = {};

    analyzeBtn.addEventListener('click', analyzeVideo);
    videoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeVideo();
    });

    async function analyzeVideo() {
        const url = videoInput.value.trim();
        
        if (!url) {
            showToast('Please enter a video URL', 'error');
            return;
        }

        if (!isValidUrl(url)) {
            showToast('Please enter a valid YouTube URL', 'error');
            return;
        }

        inputSection.style.display = 'none';
        loadingSection.style.display = 'block';
        resultsSection.style.display = 'none';

        try {
            const response = await fetch('/api/process_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to process video');
            }

            currentData = {
                title: data.metadata.title,
                summary: data.summary,
                quiz: data.quiz
            };

            displayResults(data);
            showToast('Video analyzed successfully!', 'success');

        } catch (error) {
            console.error('Error:', error);
            showToast(error.message, 'error');
            inputSection.style.display = 'block';
        } finally {
            loadingSection.style.display = 'none';
        }
    }

    function isValidUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
    }

    function displayResults(data) {
        resultsSection.style.display = 'block';

        if (data.metadata) {
            const meta = data.metadata;
            videoMeta.innerHTML = `
                ${meta.thumbnail ? `<img src="${meta.thumbnail}" alt="${meta.title}" class="video-thumbnail">` : ''}
                <div class="video-info">
                    <h3>${escapeHtml(meta.title)}</h3>
                    <p>${escapeHtml(meta.channel || 'Unknown Channel')}</p>
                    ${meta.duration ? `<span>${formatDuration(meta.duration)}</span>` : ''}
                    ${meta.view_count ? `<span>${formatNumber(meta.view_count)} views</span>` : ''}
                </div>
            `;
        }

        if (data.summary) {
            displaySummary(data.summary);
        }

        if (data.quiz && data.quiz.length > 0) {
            displayQuiz(data.quiz);
        }
    }

    function displaySummary(summary) {
        let html = '';
        
        if (summary.full_summary) {
            html = formatMarkdown(summary.full_summary);
        }

        summaryContent.innerHTML = html || '<p>No summary available</p>';

        if (summary.key_points && summary.key_points.length > 0) {
            let keyPointsHtml = '';
            summary.key_points.forEach((point, index) => {
                keyPointsHtml += `
                    <div class="key-point">
                        <div class="key-point-icon">${index + 1}</div>
                        <span>${escapeHtml(point)}</span>
                    </div>
                `;
            });
            keyPointsContent.innerHTML = keyPointsHtml;
        }
    }

    function formatMarkdown(text) {
        let html = text
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/^\- (.*$)/gm, '<li>$1</li>')
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
        html = html.replace(/<\/ul><ul>/g, '');
        
        return `<p>${html}</p>`;
    }

    function displayQuiz(questions) {
        document.getElementById('quizCount').textContent = `${questions.length} Questions`;
        
        let html = '';
        questions.forEach((q, index) => {
            html += `
                <div class="quiz-question" data-question="${index}">
                    <div class="question-header">
                        <div class="question-number">${index + 1}</div>
                        <div class="question-text">${escapeHtml(q.question)}</div>
                    </div>
                    <div class="quiz-options">
                        ${q.options.map((opt, optIndex) => `
                            <div class="quiz-option" data-question="${index}" data-option="${opt}">
                                <div class="option-label">${String.fromCharCode(65 + optIndex)}</div>
                                <span>${escapeHtml(opt)}</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="explanation" id="explanation-${index}">
                        <strong>Explanation:</strong> ${escapeHtml(q.explanation || 'This is the correct answer based on the video content.')}
                    </div>
                </div>
            `;
        });

        quizContent.innerHTML = html;
        document.getElementById('quizActions').style.display = 'flex';
        
        document.querySelectorAll('.quiz-option').forEach(opt => {
            opt.addEventListener('click', selectOption);
        });
    }

    function selectOption(e) {
        const option = e.currentTarget;
        const questionIndex = option.dataset.question;
        const selectedValue = option.dataset.option;

        document.querySelectorAll(`.quiz-option[data-question="${questionIndex}"]`).forEach(opt => {
            opt.classList.remove('selected');
        });
        
        option.classList.add('selected');
        userAnswers[questionIndex] = selectedValue;
    }

    document.getElementById('submitQuizBtn').addEventListener('click', submitQuiz);
    document.getElementById('resetQuizBtn').addEventListener('click', resetQuiz);

    function submitQuiz() {
        const questions = currentData.quiz;
        let correct = 0;

        questions.forEach((q, index) => {
            const userAnswer = userAnswers[index];
            const correctAnswer = q.correct_answer;
            const options = document.querySelectorAll(`.quiz-option[data-question="${index}"]`);
            
            options.forEach(opt => {
                if (opt.dataset.option === correctAnswer) {
                    opt.classList.add('correct');
                } else if (opt.dataset.option === userAnswer && userAnswer !== correctAnswer) {
                    opt.classList.add('incorrect');
                }
                opt.style.pointerEvents = 'none';
            });

            document.getElementById(`explanation-${index}`).classList.add('show');

            if (userAnswer === correctAnswer) {
                correct++;
            }
        });

        document.getElementById('quizScore').style.display = 'inline';
        document.getElementById('scoreValue').textContent = correct;
        document.getElementById('totalValue').textContent = questions.length;
        
        document.getElementById('submitQuizBtn').style.display = 'none';
        document.getElementById('resetQuizBtn').style.display = 'inline-flex';

        const percentage = (correct / questions.length) * 100;
        if (percentage >= 80) {
            showToast(`Excellent! You scored ${correct}/${questions.length}!`, 'success');
        } else if (percentage >= 50) {
            showToast(`Good effort! You scored ${correct}/${questions.length}`, 'warning');
        } else {
            showToast(`Keep learning! You scored ${correct}/${questions.length}`, 'error');
        }
    }

    function resetQuiz() {
        userAnswers = {};
        displayQuiz(currentData.quiz);
        document.getElementById('quizScore').style.display = 'none';
        document.getElementById('submitQuizBtn').style.display = 'inline-flex';
        document.getElementById('resetQuizBtn').style.display = 'none';
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab + 'Tab').classList.add('active');
        });
    });

    document.getElementById('downloadSummaryBtn').addEventListener('click', downloadSummary);
    document.getElementById('downloadQuizBtn').addEventListener('click', downloadQuiz);

    async function downloadSummary() {
        try {
            const response = await fetch('/api/download/summary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: currentData.title,
                    summary: currentData.summary
                })
            });

            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentData.title.substring(0, 30)}_summary.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            showToast('Summary PDF downloaded!', 'success');
        } catch (error) {
            showToast('Failed to download PDF', 'error');
        }
    }

    async function downloadQuiz() {
        try {
            const response = await fetch('/api/download/quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: currentData.title,
                    questions: currentData.quiz
                })
            });

            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentData.title.substring(0, 30)}_quiz.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            showToast('Quiz PDF downloaded!', 'success');
        } catch (error) {
            showToast('Failed to download PDF', 'error');
        }
    }

    chatbotToggle.addEventListener('click', () => {
        chatbotWindow.classList.toggle('open');
    });

    chatbotClose.addEventListener('click', () => {
        chatbotWindow.classList.remove('open');
    });

    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    async function sendChatMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addChatMessage(message, 'user');
        chatInput.value = '';

        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-message bot typing';
        typingIndicator.innerHTML = `
            <div class="message-avatar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                </svg>
            </div>
            <div class="message-content"><p>Thinking...</p></div>
        `;
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            typingIndicator.remove();

            if (data.success) {
                addChatMessage(data.response, 'bot');
            } else {
                addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            typingIndicator.remove();
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }

    function addChatMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${type === 'bot' ? 
                        '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/>' :
                        '<circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 1 0-16 0"/>'
                    }
                </svg>
            </div>
            <div class="message-content"><p>${escapeHtml(text)}</p></div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.getElementById('toastContainer').appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }

    function formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
});
