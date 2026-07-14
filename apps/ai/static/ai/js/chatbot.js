console.log("CHATBOT JS LOADED");

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(

                    cookie.substring(name.length + 1)

                );

                break;

            }

        }

    }

    return cookieValue;

}
// ======================================
// MediCore AI Chatbot
// ======================================

const aiFab = document.getElementById("aiFab");

const chatWindow = document.getElementById("chatWindow");

const closeChat = document.getElementById("closeChat");

const sendBtn = document.getElementById("sendBtn");

const chatInput = document.getElementById("chatInput");

const chatBody = document.getElementById("chatBody");


// ======================================
// Open Chat
// ======================================

aiFab.addEventListener("click", () => {

    chatWindow.style.display = "flex";

    chatInput.focus();

});


// ======================================
// Close Chat
// ======================================

closeChat.addEventListener("click", () => {

    chatWindow.style.display = "none";

});


// ======================================
// Enter Key
// ======================================

chatInput.addEventListener("keydown", function(e){

    if(e.key==="Enter"){

        e.preventDefault();

        sendMessage();

    }

});


// ======================================
// Send Button
// ======================================

sendBtn.addEventListener("click", sendMessage);


// ======================================
// Send Message
// ======================================

async function sendMessage(){

    const message = chatInput.value.trim();

    if(message===""){

        return;

    }

    addUserMessage(message);

    chatInput.value="";

    const thinking = addAIMessage("⏳ Thinking...");

    try{
        console.log("Before Fetch");

        const response = await fetch(

            "/ai/api/chat/",

            {

                method:"POST",

                headers:{

                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")

                },

                body:JSON.stringify({

                    message:message

                })

            }

        );
        console.log(response.status);
        if (!response.ok) {
            throw new Error(await response.text());

         }

        const data = await response.json();

        thinking.remove();

        addAIMessage(

            data.reply || "No response."

        );

    }

    catch(error){

        console.error(error);

        thinking.remove();

        addAIMessage(

            "⚠️ Unable to connect."

        );

    }

}


// ======================================
// User Bubble
// ======================================

function addUserMessage(text){

    const div = document.createElement("div");

    div.className="user-message";

    div.innerText=text;

    chatBody.appendChild(div);

    scrollBottom();

}


// ======================================
// AI Bubble
// ======================================

function addAIMessage(text){

    const div=document.createElement("div");

    div.className="ai-message";

    div.innerText=text;

    chatBody.appendChild(div);

    scrollBottom();

    return div;

}





// ======================================
// Auto Scroll
// ======================================

function scrollBottom(){

    chatBody.scrollTop=

    chatBody.scrollHeight;

}