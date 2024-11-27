// app.js
class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
        this.suggestions = [];
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })

        // Event delegation for dynamic buttons
        chatBox.addEventListener('click', (event) => {
            if (event.target.classList.contains('option-button')) {
                const text = event.target.innerText;
                this.messages.push({ name: "User", message: text });
                this.updateChatText(chatBox);
                this.fetchResponse(text, chatBox);
            }
        });

        // Load suggestions from the server
        this.loadSuggestions();

        // Add event listener for the input field
        const inputField = chatBox.querySelector('input');
        inputField.addEventListener('input', () => this.onInputChange(chatBox));
    }

    loadSuggestions() {
        fetch('http://127.0.0.1:5000/suggestions')
            .then(response => response.json())
            .then(data => {
                this.suggestions = data;
            })
            .catch(error => console.error('Error loading suggestions:', error));
    }

    onInputChange(chatbox) {
        const inputField = chatbox.querySelector('input');
        const query = inputField.value.toLowerCase();
    
        if (query.length === 0) {
            this.closeSuggestions(chatbox);
            return;
        }
    
        const matchedSuggestions = this.suggestions.filter(suggestion =>
            suggestion.toLowerCase().includes(query)
        ).slice(0, 5); // Limit to 5 suggestions        
    
        this.showSuggestions(chatbox, matchedSuggestions);
    }

    showSuggestions(chatbox, suggestions) {
        this.closeSuggestions(chatbox); // Close any existing suggestions

        if (suggestions.length === 0) return;

        const suggestionList = document.createElement('ul');
        suggestionList.classList.add('suggestion-list');

        suggestions.forEach(suggestion => {
            const suggestionItem = document.createElement('li');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.textContent = suggestion;
            suggestionItem.addEventListener('click', () => {
                chatbox.querySelector('input').value = suggestion;
                this.closeSuggestions(chatbox);
            });
            suggestionList.appendChild(suggestionItem);
        });

        const footer = chatbox.querySelector('.chatbox__footer');
        footer.appendChild(suggestionList);
    }

    closeSuggestions(chatbox) {
        const existingList = chatbox.querySelector('.suggestion-list');
        if (existingList) {
            existingList.remove();
        }
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        this.messages.push({ name: "User", message: text1 });
        this.updateChatText(chatbox)
        this.fetchResponse(text1, chatbox)
        textField.value = ''
    }

    fetchResponse(text, chatbox) {
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            let msg = { name: "iSuperPal", message: r.answer, options: r.options };
            this.messages.push(msg);
            this.updateChatText(chatbox)
        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
        });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "iSuperPal") {
                html += '<div class="messages__item messages__item--visitor">' + item.message;
                if (item.options && item.options.length > 0) {
                    html += '<div class="options">';
                    item.options.forEach(function(option) {
                        html += '<button class="option-button">' + option + '</button>';
                    });
                    html += '</div>';
                }
                html += '</div>';
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

const chatbox = new Chatbox();
chatbox.display();
