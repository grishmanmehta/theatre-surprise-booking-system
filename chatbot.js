// Chatbot functionality - FIXED QUICK QUESTIONS TIMING
document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWidget = document.getElementById('chatbot-widget');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotMessageInput = document.getElementById('chatbot-message');
    const chatbotSend = document.getElementById('chatbot-send');
    const quickQuestionBtns = document.querySelectorAll('.quick-question-btn');

    let isChatbotOpen = false;
    let messageCount = 0;
    let quickQuestionsVisible = true;

    // Initialize chatbot
    function initChatbot() {
        // Add welcome message
        addBotMessage("Hello! I'm your Theatre Booking Assistant! 🎭 I can help you with booking, pricing, theatre locations, customization options, and any questions about creating magical surprises. How can I assist you today?");

        // Show quick questions after a longer delay
        setTimeout(() => {
            if (quickQuestionsVisible) {
                showQuickQuestions();
            }
        }, 2000);
    }
    // Close quick questions when close button is clicked
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('quick-questions-close')) {
            hideQuickQuestions();
        }
    });

    // Add toggle button for quick questions (optional - if you want to show/hide)
    function addQuickQuestionsToggle() {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'quick-questions-toggle';
        toggleBtn.textContent = '💡 Show suggested questions';
        toggleBtn.addEventListener('click', showQuickQuestions);

        const inputArea = document.getElementById('chatbot-input-area');
        inputArea.appendChild(toggleBtn);
    }

    // Initialize toggle button (call this in initChatbot if you want the toggle feature)
    // addQuickQuestionsToggle();
    // Show quick questions
    function showQuickQuestions() {
        const quickQuestionsContainer = document.querySelector('.quick-questions-container');
        if (quickQuestionsContainer) {
            quickQuestionsContainer.style.display = 'block';
            quickQuestionsVisible = true;
        }
    }

    // Hide quick questions
    function hideQuickQuestions() {
        const quickQuestionsContainer = document.querySelector('.quick-questions-container');
        if (quickQuestionsContainer) {
            quickQuestionsContainer.style.display = 'none';
            quickQuestionsVisible = false;
        }
    }

    // Toggle quick questions
    function toggleQuickQuestions() {
        if (quickQuestionsVisible) {
            hideQuickQuestions();
        } else {
            showQuickQuestions();
        }
    }

    // Toggle chatbot
    chatbotToggle.addEventListener('click', function() {
        isChatbotOpen = !isChatbotOpen;
        if (isChatbotOpen) {
            chatbotWidget.style.display = 'flex';
            chatbotToggle.classList.add('active');
            chatbotMessageInput.focus();

            // Initialize if first time
            if (messageCount === 0) {
                initChatbot();
            }
        } else {
            chatbotWidget.style.display = 'none';
            chatbotToggle.classList.remove('active');
        }
    });

    // Close chatbot
    chatbotClose.addEventListener('click', function() {
        isChatbotOpen = false;
        chatbotWidget.style.display = 'none';
        chatbotToggle.classList.remove('active');
    });

    // Send message function
    function sendMessage(messageText = null) {
        const message = messageText || chatbotMessageInput.value.trim();

        if (message) {
            // Hide quick questions when user sends a message
            hideQuickQuestions();

            // Add user message
            addUserMessage(message);
            chatbotMessageInput.value = '';

            // Show typing indicator
            const typingIndicator = addTypingIndicator();

            // Send to backend
            fetch('/chatbot/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Remove typing indicator
                typingIndicator.remove();

                if (data.bot_response) {
                    addBotMessage(data.bot_response);
                } else {
                    addBotMessage("I apologize, but I'm having trouble responding right now. Please try asking your question again or contact our support team.");
                }

                // Show quick questions again after a longer delay (5 seconds)
                setTimeout(() => {
                    if (isChatbotOpen && quickQuestionsVisible) {
                        showQuickQuestions();
                    }
                }, 5000);
            })
            .catch(error => {
                console.error('Error:', error);
                typingIndicator.remove();
                addBotMessage("I'm sorry, I'm having connection issues right now. Please try again in a moment or refresh the page.");

                // Show quick questions again after error
                setTimeout(() => {
                    if (isChatbotOpen && quickQuestionsVisible) {
                        showQuickQuestions();
                    }
                }, 3000);
            });

            messageCount++;
        }
    }

    // Send message on button click
    chatbotSend.addEventListener('click', function() {
        sendMessage();
    });

    // Send message on Enter key
    chatbotMessageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Quick question buttons
    quickQuestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            sendMessage(question);
        });
    });

    // Add user message to chat
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${escapeHtml(message)}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Add bot message to chat
    function addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${formatBotMessage(message)}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Add typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="typing-text">Assistant is typing...</span>
                </div>
            </div>
        `;
        chatbotMessages.appendChild(typingDiv);
        scrollToBottom();
        return typingDiv;
    }

    // Format bot message with proper line breaks and styling
    function formatBotMessage(message) {
        // Convert markdown-style **bold** to HTML
        let formatted = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Convert line breaks to proper HTML
        formatted = formatted.replace(/\n/g, '<br>');

        // Add emoji styling
        formatted = formatted.replace(/🎭|🎬|🎂|💐|🍫|🎈|✨|💖|🎉|🏙️|🎦|💰|💵|⏰|📅|📸|🎊|💝|🌟|💑|💍|💕|🎓|🏆/g,
            match => `<span class="emoji">${match}</span>`);

        return formatted;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Get current time in HH:MM format
    function getCurrentTime() {
        return new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    // Scroll to bottom of chat
    function scrollToBottom() {
        setTimeout(() => {
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }, 100);
    }

    // Auto-focus input when chatbot opens
    chatbotToggle.addEventListener('click', function() {
        if (isChatbotOpen) {
            setTimeout(() => {
                chatbotMessageInput.focus();
            }, 300);
        }
    });

    // Handle clicks outside chatbot to close (optional)
    document.addEventListener('click', function(event) {
        if (isChatbotOpen &&
            !chatbotWidget.contains(event.target) &&
            !chatbotToggle.contains(event.target)) {
            isChatbotOpen = false;
            chatbotWidget.style.display = 'none';
            chatbotToggle.classList.remove('active');
        }
    });

    // Prevent propagation for chatbot clicks
    chatbotWidget.addEventListener('click', function(event) {
        event.stopPropagation();
    });
});