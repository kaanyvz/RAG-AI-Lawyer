document.addEventListener("DOMContentLoaded", function () {
    const apiKeyInput = document.getElementById("api-key");
    const saveKeyButton = document.getElementById("save-key-btn");
    const newChatButton = document.getElementById("new-chat-btn");
    const userQuestionInput = document.getElementById("user-question");
    const getResponseButton = document.getElementById("get-response-btn");
    const chatConversation = document.getElementById('chat-conversation');
    const pineconeIndexDropdown = document.getElementById("pinecone-index-dropdown");


    let openaiApiKey = null;
    let chatHistory = [];

    // Function to fetch chat history files and update dropdown

    newChatButton.disabled = true;
    newChatButton.classList.add("blocked");
    pineconeIndexDropdown.disabled = true;
    pineconeIndexDropdown.classList.add("blocked");
    const updateChatHistoryButtons = async () => {
        const response = await fetch(
            `http://localhost:8000/get_chat_history_files?openai_api_key=${openaiApiKey}`);
        const data = await response.json();

        const chatHistoryButtonsContainer = document.getElementById("chat-history-buttons");
        chatHistoryButtonsContainer.innerHTML = "";

        data.chat_history_files.forEach((file) => {

            const chatHistoryButton = document.createElement("button");
            let chatTitle = file.title;
            if (chatTitle.length > 15){
                chatTitle = chatTitle.slice(0, 15) + "...";
            }
            chatHistoryButton.textContent = chatTitle;
            chatHistoryButton.className = "chat-history-button";
            chatHistoryButton.value = file.id;
            chatHistoryButton.addEventListener("click", () => {
                const allChatHistoryButtons = document.querySelectorAll(".chat-history-button");
                allChatHistoryButtons.forEach((button) => {
                    button.classList.remove("selected-chat-history-button");
                });

                // Add the selected class to the clicked button
                chatHistoryButton.classList.add("selected-chat-history-button");

                loadChatHistory(file.id);
            });

            const updateButton = document.createElement("button");
            const updateImage = document.createElement("img");
            updateImage.src = "edit.png";
            updateImage.classList = "update-button-image";
            updateButton.className = "update-button";
            updateButton.appendChild(updateImage);
            updateButton.addEventListener("click", async () => {
                const newTitle = prompt("Edit this conversation title");
                if (newTitle) {
                    const response = await fetch(
                        `http://localhost:8000/update_chat_title?chat_history_id=${file.id}&chat_title=${newTitle}`, {
                        method: "POST",
                    });
                    const data = await response.json();
                    console.log(data.message);
                    updateChatHistoryButtons();
                }
            });

            const deleteButton = document.createElement("button");
            const deleteImage = document.createElement("img");
            deleteImage.src = "delete.png";
            deleteImage.classList = "delete-button-image";
            deleteButton.className = "delete-button";
            deleteButton.appendChild(deleteImage);
            deleteButton.addEventListener("click", async () => {
                const confirmation = confirm("Are you sure you want to delete this conversation?");
                if(confirmation){
                    const response = await fetch(
                    `http://localhost:8000/delete_chat_history/${file.id}`, {
                            method: "DELETE",
                    });
                    const data = await response.json();
                    console.log(data.message);
                    updateChatHistoryButtons();
                }

            });

            chatHistoryButtonsContainer.appendChild(chatHistoryButton);
            chatHistoryButtonsContainer.appendChild(updateButton);
            chatHistoryButtonsContainer.appendChild(deleteButton);
        });
    };

    // Function to load chat history into main content
    const loadChatHistory = async (file) => {
        const loadingMessage = document.getElementById("loading-message");
        const chatConversation = document.getElementById('chat-conversation');

        loadingMessage.style.display = "block"; // Show loading message
        chatConversation.style.display = "none"; // Hide chat conversation

        const response = await fetch(`http://localhost:8000/select_chat_history?chat_history_id=${file}`, {
            method: "POST",
        });
        const data = await response.json();

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

        loadingMessage.style.display = "none"; // Hide loading message
        chatConversation.style.display = "block"; // Show chat conversation

        return data.chat_history; // Ensure that the function returns the chat history data
    };
    // Function to create new chat history
    const createNewChat = async () => {
        const newChatText = document.getElementById("new-chat-text");
        const newChatSpinner = document.getElementById("new-chat-spinner");

        newChatText.style.display = "none";
        newChatSpinner.style.display = "block";

        const response = await fetch("http://localhost:8000/create_new_chat", {
            method: "POST",
        });
        const data = await response.json();
        console.log(data.message);
        updateChatHistoryButtons();

        newChatText.style.display = "block";
        newChatSpinner.style.display = "none";
    };


    // Function to save API key
    const saveApiKey = async () => {
        openaiApiKey = apiKeyInput.value.trim();
        if (openaiApiKey) {
            const saveText = document.getElementById("save-text");
            const saveSpinner = document.getElementById("save-spinner");

            // Hide the save text and show the spinner
            saveText.style.display = "none";
            saveSpinner.style.display = "block";
            const response = await fetch("http://localhost:8000/set_api_key", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ openai_api_key: openaiApiKey }),
            });
            if(response.status === 200){
                const data = await response.json();
                console.log(data.message);
                updateChatHistoryButtons();
                newChatButton.disabled = false;
                newChatButton.classList.remove("blocked");
                pineconeIndexDropdown.disabled = false;
                pineconeIndexDropdown.classList.remove("blocked");
            }else{
                alert("Error: Invalid OpenAI API Key.");
            }
             // Hide the spinner and show the save text
            saveText.style.display = "block";
            saveSpinner.style.display = "none";

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
