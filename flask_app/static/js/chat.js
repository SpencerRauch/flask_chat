console.log('hello')
let user = null

const socket = io();
const currentChat = document.querySelector('#current_chat')

async function getUser() {
    let response = await fetch('/api/users/get_logged_user')
    let user_data = await response.json()
    user = user_data
}

getUser()

function send(event) {
    event.preventDefault()
    let message_content = event.target.message.value
    let message = { 'username': user.username, 'content': message_content, 'created_at': new Date().toLocaleString() }
    socket.emit('new_message', message)
    event.target.message.value = "";
}

socket.on("connect", () => {
    console.log(socket.id); // x8WIv7-mJelg7on_ALbx
});

socket.on('chat_history', (response) => {
    console.log(response)
    for (let message of response.data) {
        currentChat.innerHTML += `<p>${message.username} at ${message.created_at}: ${message.content}</p>`
    }
})

socket.on('message_added', (message) => {
    console.log('received message from server')
    currentChat.innerHTML += `<p>${message.username} at ${message.created_at}: ${message.content}</p>`
    currentChat.lastChild.scrollIntoView();
})


