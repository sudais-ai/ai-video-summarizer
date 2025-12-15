// Global variables
let currentSummary = null;
let currentQuiz = null;

// Scroll to input section
function scrollToInput() {
    document.getElementById('input').scrollIntoView({ behavior: 'smooth' });
}

// Start demo with sample video
function startDemo() {
    document.getElementById('videoUrl').value = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
    processVideo();
}

// Handle file upload
function handleFileUpload(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.size > 500 * 1024 * 1024) {
            alert('File size must be less than 500MB');
            return;
        }
        
        // Show loading
        showLoading();
        
        // Simulate processing for demo
        setTimeout(() => {
            hideLoading();
            showResults(generateDemoData());
            createConfetti();
        }, 3000);
    }
}

// Process video from URL
async function processVideo() {
    const url = document.getElementById('videoUrl').value.trim();
    const processBtn = document.getElementById('processBtn');
    
    if (!url && !document.getElementById('fileInput').files[0]) {
        alert('Please enter a video URL or upload a file');
        return;
    }
    
    // Show loading animation
    showLoading();
    
    try {
        // In a real implementation, this would call your backend API
        // For now, we'll use demo data
        await simulateAPIRequest();
        
        // Hide loading and show results
        hideLoading();
        
        // Generate and display demo results
        const demoData = generateDemoData();
        showResults(demoData);
        
        // Add confetti effect
        createConfetti();
        
        // Update stats with animation
        animateStats();
        
    } catch (error) {
        hideLoading();
        alert('Error processing video: ' + error.message);
    }
}

// Show loading overlay
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'flex';
    
    // Animate progress bar
    const progress = document.querySelector('.progress');
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 100) {
            clearInterval(interval);
        } else {
            width += Math.random() * 10;
            progress.style.width = Math.min(width, 100) + '%';
        }
    }, 200);
}

// Hide loading overlay
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
    document.querySelector('.progress').style.width = '0%';
}

// Simulate API request delay
function simulateAPIRequest() {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve();
        }, 3000);
    });
}

// Generate demo data for testing
function generateDemoData() {
    const summaries = [
        "This video discusses the fundamentals of machine learning, including supervised and unsupervised learning approaches.",
        "Key concepts covered include neural networks, backpropagation, and gradient descent optimization techniques.",
        "The instructor explains how to preprocess data and evaluate model performance using metrics like accuracy and F1-score.",
        "Practical examples demonstrate how to implement a simple classifier using Python and scikit-learn library.",
        "The video concludes with best practices for avoiding overfitting and improving model generalization."
    ];
    
    const quizQuestions = [
        {
            type: 'mcq',
            question: 'What is the primary goal of supervised learning?',
            options: ['To discover hidden patterns', 'To make predictions based on labeled data', 'To reduce data dimensionality', 'To visualize complex datasets'],
            correct_answer: 'To make predictions based on labeled data',
            explanation: 'Supervised learning uses labeled data to train models for making predictions.'
        },
        {
            type: 'mcq',
            question: 'Which algorithm is commonly used for classification tasks?',
            options: ['K-Means', 'Random Forest', 'PCA', 'DBSCAN'],
            correct_answer: 'Random Forest',
            explanation: 'Random Forest is an ensemble method effective for classification problems.'
        },
        {
            type: 'true_false',
            question: 'Neural networks always require large amounts of training data.',
            options: ['True', 'False'],
            correct_answer: 'False',
            explanation: 'While neural networks often benefit from large datasets, they can work with smaller datasets using techniques like transfer learning.'
        },
        {
            type: 'mcq',
            question: 'What does the term "overfitting" refer to?',
            options: ['Model is too simple', 'Model performs well on training but poorly on new data', 'Model ignores important features', 'Training takes too long'],
            correct_answer: 'Model performs well on training but poorly on new data',
            explanation: 'Overfitting occurs when a model learns the training data too well, including noise, and fails to generalize.'
        }
    ];
    
    return {
        summary: summaries,
        quiz: quizQuestions,
        metadata: {
            duration: '15:42',
            title: 'Introduction to Machine Learning Fundamentals',
            language: 'English'
        }
    };
}

// Display results on the page
function showResults(data) {
    currentSummary = data.summary;
    currentQuiz = data.quiz;
    
    // Show results container
    document.getElementById('resultsContainer').style.display = 'block';
    
    // Populate summary
    const summaryContent = document.getElementById('summaryContent');
    summaryContent.innerHTML = `
        <div class="video-metadata">
            <p><strong>Title:</strong> ${data.metadata.title}</p>
            <p><strong>Duration:</strong> ${data.metadata.duration}</p>
            <p><strong>Language:</strong> ${data.metadata.language}</p>
        </div>
        <h3 style="margin-bottom: 15px; color: var(--primary-blue);">Key Points:</h3>
    `;
    
    data.summary.forEach((point, index) => {
        summaryContent.innerHTML += `
            <div class="key-point">
                <i class="fas fa-check-circle"></i>
                <span>${point}</span>
            </div>
        `;
    });
    
    // Populate quiz
    const quizContent = document.getElementById('quizContent');
    quizContent.innerHTML = '';
    
    data.quiz.forEach((question, qIndex) => {
        const questionHtml = `
            <div class="quiz-question" id="question${qIndex}">
                <h4 style="margin-bottom: 15px;">Q${qIndex + 1}: ${question.question}</h4>
                ${generateOptionsHtml(question, qIndex)}
                <div class="explanation" id="explanation${qIndex}">
                    <strong><i class="fas fa-lightbulb"></i> Explanation:</strong> ${question.explanation}
                </div>
            </div>
        `;
        quizContent.innerHTML += questionHtml;
    });
    
    // Scroll to results
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
}

// Generate HTML for quiz options
function generateOptionsHtml(question, qIndex) {
    let html = '';
    
    if (question.type === 'mcq') {
        question.options.forEach((option, oIndex) => {
            const optionId = `q${qIndex}o${oIndex}`;
            html += `
                <div class="option" onclick="selectAnswer(${qIndex}, ${oIndex})">
                    <input type="radio" id="${optionId}" name="question${qIndex}" value="${option}">
                    <label class="option-label" for="${optionId}">${String.fromCharCode(65 + oIndex)}</label>
                    <span>${option}</span>
                </div>
            `;
        });
    } else if (question.type === 'true_false') {
        question.options.forEach((option, oIndex) => {
            const optionId = `q${qIndex}o${oIndex}`;
            html += `
                <div class="option" onclick="selectAnswer(${qIndex}, ${oIndex})">
                    <input type="radio" id="${optionId}" name="question${qIndex}" value="${option}">
                    <label class="option-label" for="${optionId}">${option.charAt(0)}</label>
                    <span>${option}</span>
                </div>
            `;
        });
    }
    
    return html;
}

// Handle answer selection
function selectAnswer(qIndex, oIndex) {
    const question = currentQuiz[qIndex];
    const selectedOption = question.options[oIndex];
    const questionElement = document.getElementById(`question${qIndex}`);
    const explanationElement = document.getElementById(`explanation${qIndex}`);
    
    // Show explanation
    explanationElement.style.display = 'block';
    
    // Mark as correct or incorrect
    if (selectedOption === question.correct_answer) {
        questionElement.classList.add('correct-answer');
        questionElement.classList.remove('incorrect-answer');
        
        // Add confetti for correct answer
        createMiniConfetti(questionElement);
    } else {
        questionElement.classList.add('incorrect-answer');
        questionElement.classList.remove('correct-answer');
    }
    
    // Highlight correct answer
    const options = questionElement.querySelectorAll('.option');
    options.forEach((option, index) => {
        if (question.options[index] === question.correct_answer) {
            option.style.backgroundColor = 'rgba(76, 175, 80, 0.2)';
            option.style.borderLeft = '3px solid var(--success-green)';
        }
    });
}

// Animate stats counter
function animateStats() {
    const videosElement = document.getElementById('videosProcessed');
    const questionsElement = document.getElementById('questionsGenerated');
    const timeElement = document.getElementById('timeSaved');
    
    animateCounter(videosElement, 1247);
    animateCounter(questionsElement, 8592);
    animateCounter(timeElement, 2154);
}

// Animate number counter
function animateCounter(element, target) {
    let current = parseInt(element.textContent.replace(/,/g, ''));
    const increment = Math.ceil((target - current) / 50);
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = current.toLocaleString();
    }, 30);
}

// Create confetti effect
function createConfetti() {
    const colors = ['#1A73E8', '#FF9800', '#4CAF50', '#E53935'];
    
    for (let i = 0; i < 150; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.width = Math.random() * 10 + 5 + 'px';
        confetti.style.height = confetti.style.width;
        
        const animation = confetti.animate([
            { top: '0px', opacity: 1, transform: 'rotate(0deg)' },
            { top: '100vh', opacity: 0, transform: 'rotate(360deg)' }
        ], {
            duration: Math.random() * 3000 + 2000,
            easing: 'cubic-bezier(0.215, 0.61, 0.355, 1)'
        });
        
        document.body.appendChild(confetti);
        
        animation.onfinish = () => {
            confetti.remove();
        };
    }
}

// Create mini confetti for correct answers
function createMiniConfetti(element) {
    const rect = element.getBoundingClientRect();
    const colors = ['#4CAF50', '#FF9800', '#1A73E8'];
    
    for (let i = 0; i < 30; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = (rect.left + Math.random() * rect.width) + 'px';
        confetti.style.top = (rect.top + Math.random() * rect.height) + 'px';
        confetti.style.width = '8px';
        confetti.style.height = '8px';
        confetti.style.position = 'fixed';
        
        document.body.appendChild(confetti);
        
        const animation = confetti.animate([
            { transform: 'translate(0, 0) rotate(0deg)', opacity: 1 },
            { transform: `translate(${Math.random() * 100 - 50}px, -50px) rotate(180deg)`, opacity: 0 }
        ], {
            duration: 1000,
            easing: 'cubic-bezier(0.215, 0.61, 0.355, 1)'
        });
        
        animation.onfinish = () => {
            confetti.remove();
        };
    }
}

// Download summary as PDF
function downloadSummary() {
    if (!currentSummary) {
        alert('Please generate a summary first');
        return;
    }
    
    // In a real implementation, this would generate and download a PDF summary
    // Implementation would use a PDF generation library like jsPDF
    
    alert('PDF download feature would be implemented with jsPDF library\nSummary saved as: video_summary.pdf');
}

// Download quiz as PDF
function downloadQuiz() {
    if (!currentQuiz) {
        alert('Please generate a quiz first');
        return;
    }
    
    // In a real implementation, this would generate and download a PDF quiz
    // Implementation would use a PDF generation library like jsPDF
    
    alert('PDF download feature would be implemented with jsPDF library\nQuiz saved as: video_quiz.pdf');
}

// Initialize page with animated stats
document.addEventListener('DOMContentLoaded', function() {
    animateStats();
    
    // Add floating background shapes
    createBackgroundShapes();
    
    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});

// Create floating background shapes
function createBackgroundShapes() {
    const shapesContainer = document.createElement('div');
    shapesContainer.id = 'background-shapes';
    shapesContainer.style.position = 'fixed';
    shapesContainer.style.top = '0';
    shapesContainer.style.left = '0';
    shapesContainer.style.width = '100%';
    shapesContainer.style.height = '100%';
    shapesContainer.style.pointerEvents = 'none';
    shapesContainer.style.zIndex = '-1';
    shapesContainer.style.overflow = 'hidden';
    
    for (let i = 0; i < 15; i++) {
        const shape = document.createElement('div');
        shape.style.position = 'absolute';
        shape.style.width = Math.random() * 100 + 50 + 'px';
        shape.style.height = shape.style.width;
        shape.style.background = `rgba(${Math.random() * 50}, ${Math.random() * 100 + 100}, ${Math.random() * 100 + 150}, ${Math.random() * 0.05 + 0.02})`;
        shape.style.borderRadius = '50%';
        shape.style.left = Math.random() * 100 + '%';
        shape.style.top = Math.random() * 100 + '%';
        
        // Animate floating
        shape.animate([
            { transform: 'translate(0, 0)' },
            { transform: `translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px)` }
        ], {
            duration: Math.random() * 20000 + 10000,
            iterations: Infinity,
            direction: 'alternate',
            easing: 'ease-in-out'
        });
        
        shapesContainer.appendChild(shape);
    }
    
    document.body.appendChild(shapesContainer);
}