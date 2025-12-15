document.addEventListener('DOMContentLoaded', function() {
    const videoInput = document.getElementById('videoUrl');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const summaryContent = document.getElementById('summaryContent');
    const quizContent = document.getElementById('quizContent');
    const videoMeta = document.getElementById('videoMeta');
    
    let statsAnimated = false;
    const stats = {
        videos: 1247,
        questions: 8934,
        hours: 2156
    };

    function scrollToInput() {
        document.getElementById('inputSection').scrollIntoView({ behavior: 'smooth' });
    }

    window.scrollToInput = scrollToInput;

    function showToast(message, type = 'success') {
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type} show`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function animateCounter(element, target) {
        const duration = 2000;
        const start = 0;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + (target - start) * easeOut);
            
            element.textContent = current.toLocaleString() + '+';
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }

    function animateStats() {
        if (statsAnimated) return;
        
        const statsSection = document.querySelector('.stats-section');
        const rect = statsSection.getBoundingClientRect();
        
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            statsAnimated = true;
            
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers[0].dataset.target = stats.videos;
            statNumbers[1].dataset.target = stats.questions;
            statNumbers[2].dataset.target = stats.hours;
            
            statNumbers.forEach(el => {
                animateCounter(el, parseInt(el.dataset.target));
            });
        }
    }

    window.addEventListener('scroll', animateStats);

    function showConfetti() {
        const canvas = document.createElement('canvas');
        canvas.className = 'confetti';
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const particles = [];
        const colors = ['#1A73E8', '#FF9800', '#4CAF50', '#E53935', '#9C27B0'];
        
        for (let i = 0; i < 150; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height - canvas.height,
                size: Math.random() * 10 + 5,
                color: colors[Math.floor(Math.random() * colors.length)],
                speed: Math.random() * 3 + 2,
                rotation: Math.random() * 360,
                rotationSpeed: Math.random() * 10 - 5
            });
        }
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            let stillVisible = false;
            
            particles.forEach(p => {
                p.y += p.speed;
                p.rotation += p.rotationSpeed;
                
                if (p.y < canvas.height + 50) {
                    stillVisible = true;
                    
                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate(p.rotation * Math.PI / 180);
                    ctx.fillStyle = p.color;
                    ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
                    ctx.restore();
                }
            });
            
            if (stillVisible) {
                requestAnimationFrame(animate);
            } else {
                canvas.remove();
            }
        }
        
        animate();
    }

    async function analyzeVideo() {
        const url = videoInput.value.trim();
        
        if (!url) {
            showToast('Please enter a video URL', 'error');
            return;
        }
        
        if (!url.includes('youtube.com') && !url.includes('youtu.be') && !url.includes('vimeo.com')) {
            showToast('Please enter a valid YouTube or Vimeo URL', 'error');
            return;
        }
        
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<div class="loader"></div> Analyzing...';
        
        try {
            const response = await fetch('/api/process_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            displayResults(data);
            showToast('Video analyzed successfully!');
            showConfetti();
            
            stats.videos++;
            stats.questions += data.quiz ? data.quiz.length : 0;
            
        } catch (error) {
            showToast(error.message || 'Error analyzing video', 'error');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg> Analyze Video';
        }
    }

    function displayResults(data) {
        videoMeta.innerHTML = `
            <div class="video-info">
                <h4>${data.metadata?.title || 'Video'}</h4>
                <p>Duration: ${formatDuration(data.metadata?.duration || 0)}</p>
            </div>
        `;
        
        const summary = data.summary;
        if (summary && summary.key_points && summary.key_points.length > 0) {
            summaryContent.innerHTML = `
                <ul>
                    ${summary.key_points.map(point => `<li>${point}</li>`).join('')}
                </ul>
                <p style="margin-top: 15px; color: #666;">${summary.full_summary || ''}</p>
            `;
        } else if (summary && summary.full_summary) {
            summaryContent.innerHTML = `<p>${summary.full_summary}</p>`;
        } else {
            summaryContent.innerHTML = '<p>Summary generated from video content.</p>';
        }
        
        const quiz = data.quiz || [];
        if (quiz.length > 0) {
            quizContent.innerHTML = quiz.map((q, index) => `
                <div class="quiz-card" data-question="${index}">
                    <div class="quiz-question">${index + 1}. ${q.question}</div>
                    <div class="quiz-options">
                        ${q.options.map((opt, optIndex) => `
                            <label class="quiz-option" data-correct="${opt === q.correct_answer}">
                                <input type="radio" name="q${index}" value="${optIndex}">
                                <span>${opt}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            `).join('');
            
            document.querySelectorAll('.quiz-option').forEach(option => {
                option.addEventListener('click', function() {
                    const card = this.closest('.quiz-card');
                    card.querySelectorAll('.quiz-option').forEach(opt => {
                        opt.classList.remove('selected', 'correct', 'incorrect');
                    });
                    
                    this.classList.add('selected');
                    
                    if (this.dataset.correct === 'true') {
                        this.classList.add('correct');
                        showToast('Correct!', 'success');
                    } else {
                        this.classList.add('incorrect');
                        card.querySelector('[data-correct="true"]').classList.add('correct');
                        showToast('Try again!', 'error');
                    }
                });
            });
        } else {
            quizContent.innerHTML = '<p>No quiz questions could be generated for this video.</p>';
        }
        
        resultsSection.classList.add('active');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function formatDuration(seconds) {
        if (!seconds) return 'Unknown';
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hrs > 0) {
            return `${hrs}h ${mins}m ${secs}s`;
        }
        return `${mins}m ${secs}s`;
    }

    function downloadSummaryPDF() {
        const content = document.getElementById('summaryContent').innerText;
        const title = document.querySelector('.video-info h4')?.innerText || 'Video Summary';
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${title} - Summary</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }
                    h1 { color: #1A73E8; border-bottom: 2px solid #1A73E8; padding-bottom: 10px; }
                    p { line-height: 1.8; color: #333; }
                    .footer { margin-top: 40px; text-align: center; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <h1>${title}</h1>
                <h2>AI Generated Summary</h2>
                <div>${content}</div>
                <div class="footer">Generated by AI Video Summarizer</div>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        
        showToast('Summary ready for download!');
    }

    function downloadQuizPDF() {
        const quizCards = document.querySelectorAll('.quiz-card');
        let content = '';
        
        quizCards.forEach((card, index) => {
            const question = card.querySelector('.quiz-question').innerText;
            const options = Array.from(card.querySelectorAll('.quiz-option span')).map(opt => opt.innerText);
            
            content += `<div style="margin-bottom: 20px;">
                <p><strong>${question}</strong></p>
                <ul>
                    ${options.map(opt => `<li>${opt}</li>`).join('')}
                </ul>
            </div>`;
        });
        
        const title = document.querySelector('.video-info h4')?.innerText || 'Video Quiz';
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${title} - Quiz</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }
                    h1 { color: #1A73E8; border-bottom: 2px solid #1A73E8; padding-bottom: 10px; }
                    ul { margin-left: 20px; }
                    li { margin: 5px 0; }
                    .footer { margin-top: 40px; text-align: center; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <h1>${title}</h1>
                <h2>AI Generated Quiz</h2>
                ${content}
                <div class="footer">Generated by AI Video Summarizer</div>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        
        showToast('Quiz ready for download!');
    }

    window.downloadSummaryPDF = downloadSummaryPDF;
    window.downloadQuizPDF = downloadQuizPDF;

    analyzeBtn.addEventListener('click', analyzeVideo);
    
    videoInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeVideo();
        }
    });
});
