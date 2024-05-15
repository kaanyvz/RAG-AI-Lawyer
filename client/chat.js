document.addEventListener("DOMContentLoaded", function () {
    const apiKeyInput = document.getElementById("api-key");
    const saveKeyButton = document.getElementById("save-key-btn");
    const newChatButton = document.getElementById("new-chat-btn");
    const userQuestionInput = document.getElementById("user-question");
    const getResponseButton = document.getElementById("get-response-btn");
    const chatHistoryDropdown = document.getElementById("chat-history-dropdown");
    const chatConversation = document.getElementById('chat-conversation');
    const pineconeIndexDropdown = document.getElementById("pinecone-index-dropdown");
    const spinner = document.getElementById("spinner");


    let openaiApiKey = null;
    let chatHistory = [];

    // Function to fetch chat history files and update dropdown
    const updateChatHistoryDropdown = async () => {
        const response = await fetch("http://localhost:8000/get_chat_history_files");
        const data = await response.json();

        chatHistoryDropdown.innerHTML = "<option value=''>Select Chat History</option>";
        data.chat_history_files.forEach((file) => {
            const option = document.createElement("option");
            option.textContent = file;
            option.value = file;
            chatHistoryDropdown.appendChild(option);
        });
    };

    // Function to load chat history into main content
    const loadChatHistory = async (file) => {
        const response = await fetch("http://localhost:8000/select_chat_history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ chat_history_file: file }),
        });
        const data = await response.json();
        console.log(data); // Add this line to check the data received
        console.log(data.message);

        // Clear existing chat conversation
        chatConversation.innerHTML = "";

        // Append chat history to conversation
        data.chat_history.forEach(item => {
            const question = item[0].trim();
            const answer = item[1].trim();

            // Append user message
            appendUserMessage(question);

            // Append bot message
            appendBotMessage(answer);
        });

        return data.chat_history; // Ensure that the function returns the chat history data
    };
    // Function to create new chat history
    const createNewChat = async () => {
        const response = await fetch("http://localhost:8000/create_new_chat", {
            method: "POST",
        });
        const data = await response.json();
        console.log(data.message);
        updateChatHistoryDropdown();
    };

    // Function to save API key
    const saveApiKey = async () => {
        openaiApiKey = apiKeyInput.value.trim();
        if (openaiApiKey) {
            const response = await fetch("http://localhost:8000/set_api_key", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ openai_api_key: openaiApiKey }),
            });
            const data = await response.json();
            console.log(data.message);
            updateChatHistoryDropdown();
        } else {
            alert("Please enter your API key.");
        }
    };

    // Function to append a user message to the chat conversation
    function appendUserMessage(message) {
        const userMessage = user_template.replace("{{MSG}}", message);
        chatConversation.insertAdjacentHTML("beforeend", userMessage);
    }

    // Function to append a bot message to the chat conversation
    function appendBotMessage(message) {
        const botMessage = bot_template.replace("{{MSG}}", message);
        chatConversation.insertAdjacentHTML("beforeend", botMessage);
    }

    // Event listener for saving API key
    saveKeyButton.addEventListener("click", saveApiKey);

    // Event listener for selecting chat history from dropdown
    chatHistoryDropdown.addEventListener("change", function () {
        const selectedFile = this.value;
        if (selectedFile) {
            // Clear current chat conversation
            chatConversation.innerHTML = '';

            // Load chat history
            loadChatHistory(selectedFile).then(chatHistory => {
                // Iterate over chat history and append each message to chat conversation
                chatHistory.forEach(chat => {
                    if (chat.type === 'user') {
                        appendUserMessage(chat.message);
                    } else if (chat.type === 'bot') {
                        appendBotMessage(chat.message);
                    }
                });
            });
        }
    });

    // Event listener for creating new chat
    newChatButton.addEventListener("click", createNewChat);

    // Event listener for getting response
    getResponseButton.addEventListener("click", async () => {
        const question = userQuestionInput.value.trim();
        if (question) {
            const response = await fetch("http://localhost:8000/get_response", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question }),
            });
            const data = await response.json();
            console.log(data);
            appendToChatConversation(question, data.result.answer);
            updateUI(data);
        } else {
            alert("Please enter a question.");
        }
    });

    // Update UI with response and chat history
    const updateUI = (response) => {
        chatHistory = chatHistory.concat(response.chat_history);
    };

    // Function to append a question and answer to the chat conversation
    function appendToChatConversation(question, answer) {
        appendUserMessage(question);
        appendBotMessage(answer);
    }


    pineconeIndexDropdown.addEventListener("change", function () {
        const selectedPineconeIndex = this.value;
        if (selectedPineconeIndex) {
            setPineconeIndex(selectedPineconeIndex);
        }
    });

    const setPineconeIndex = async (indexNumber) => {
        const response = await fetch(`http://localhost:8000/set_pinecone_index?index_number=${indexNumber}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ index_number: indexNumber }),
        });
        const data = await response.json();
        console.log(data.message);
    };
});

// Bot and User message templates
const bot_template = `
<div class="chat-message bot"> 
    <div class="avatar"> 
        <img src="https://i.ibb.co/PrMBMtj/66-668806-openai-logo-openai-logo-elon-musk-hd-png.png"> 
    </div> 
    <div class="message">{{MSG}}</div>
</div>
`;

const user_template = `
<div class="chat-message user"> 
    <div class="avatar"> 
        <img src="https://i.ibb.co/gdxDh59/png-clipart-profile-logo-computer-icons-user-user-blue-heroes-thumbnail.png"> 
    </div> 
    <div class="message">{{MSG}}</div>
</div>
`;

// CSS styling
const css = `
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
    align-items: center ;
}
.chat-message.user {
    background-color: #2b313e;
}
.chat-message.bot {
    background-color: #475063;
}
.chat-message .avatar {
    width: 20%;
    margin-right: 0.5rem;
}
.chat-message .avatar img {
    max-width: 78px;
    max-height: 78px;
    border-radius: 50%;
    object-fit: cover;
}
.chat-message .message {
    width: 80%;
    padding: 0 1.5rem;
    color: #fff;
}
</style>
`;

// Append CSS to the head of the document
document.head.insertAdjacentHTML("beforeend", css);
