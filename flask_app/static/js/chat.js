/*                        Variable Declarations                            */
// these variables will keep track of our user data and the current room we're watching
let user = null
let currentRoom = null

//brings in socket io from cdn linked on template 
const socket = io();

//targetting important elements we'll use
const currentChat = document.querySelector('#current_chat')
const roomDisplay = document.querySelector('#current_room')
const joinedRoomList = document.querySelector('#rooms_joined')


/*                        Function Declarations                            */

//async function to retrieve the logged in user's info and join them to their list of joined rooms
//we call this function on connect
async function getUser() {
    let response = await fetch('/api/users/get_logged_user')
    let user_data = await response.json()
    user = user_data
    console.log(user)
    for (let room_id of user.joined_room_ids) {
        console.log('joining ', room_id)
        joinRoom(room_id)
    }
}

//function for joining a previously joined room (room in our room list)
function joinRoom(room_id) {
    socket.emit('join', {
        username: user.username,
        room: "" + room_id
    })
}

// function for joining a new room (adds it to our room list)
function joinNewRoom(room_id) {
    if (user.joined_room_ids.includes(room_id)){
        alert('Already joined')
        return
    }
    user.joined_room_ids.push(room_id)
    joinRoom(room_id)
    fetch('/api/rooms/' + room_id + '/join')
        .then(res => res.json())
        .then(data => {
            joinedRoomList.innerHTML += `
            <div class="joined_room" id="joined${room_id}">
            <p onclick="getHistory(${room_id})"><span id="newFor${room_id}" class="unreads"></span> ${data.roomname} </p>
            <button onclick="leaveRoom(${room_id})" class="btn">Leave</button>
            </div>
            `
        })
        .catch(err => console.log(err))
}

// function for leaving a room
function leaveRoom(room_id) {
    socket.emit('leave', {
        username: user.username,
        room: "" + room_id
    })
    user.joined_room_ids = user.joined_room_ids.filter(e => e != room_id)
    fetch('/api/rooms/' + room_id + '/leave')
        .then(res => res.json())
        .then(data => {
            console.log(data)
            document.querySelector("#joined" + room_id).remove()

        })
        .catch(err => console.log(err))
}

//function for handling new message submissions
function send(event) {
    event.preventDefault()
    if (currentRoom == null){ 
        alert('Select a joined room from the right')
        return
    }
    let message_content = event.target.message.value
    let message = { 'username': user.username, 'content': message_content, 'created_at': new Date().toLocaleString('en-US') }
    socket.emit('new_message', message, currentRoom)
    event.target.message.value = "";
}

//function for retrieving a room's history from the db and displaying it to page
function getHistory(room_id) {
    currentRoom = room_id
    newSpan = document.querySelector("#newFor" + room_id)
    newSpan.innerText = "";
    fetch(`/api/rooms/${room_id}/history`)
        .then(res => res.json())
        .then(data => {
            roomDisplay.innerHTML = data[0].name
            console.log('history', data)
            renderChat(data)
        })
        .catch(err => console.log('get history error', err))
}

//helper function to render chat history, gets called in getHistory
function renderChat(chat_log) {
    currentChat.innerHTML = "<p>Loading...</p>"
    //updating the DOM is expensive, so it's better to generate all the HTML and then set it only once
    let chatHTML = ""
    for (let message of chat_log) {
        chatHTML += `<p>${message.username} at ${message.created_at}: ${message.content}</p>`
    }
    currentChat.innerHTML = chatHTML
    currentChat.lastChild.scrollIntoView(); //this line scrolls our chat to the bottom
}


/*                        Socket Events                            */

//connect event happens when client connects to server, we use it as a time to get our user data 
socket.on("connect", () => {
    console.log(socket.id); // x8WIv7-mJelg7on_ALbx
    getUser()
});


// old code to get my hardcoded global chat
// socket.on('chat_history', (response) => {
//     console.log(response)
//     for (let message of response.data) {
//         currentChat.innerHTML += `<p>${message.username} at ${message.created_at}: ${message.content}</p>`
//     }
// })


//this listens for new messages being added by the server
//we should only receive messages for rooms we joined
socket.on('message_added', (message, roomFor) => {
    console.log('received message from server for room ' + roomFor)
    if (roomFor == currentRoom) { //if we got a message for the room we're currently viewing
        //we add it to the current chat view, and scroll to the bottom
        currentChat.innerHTML += `<p>${message.username} at ${message.created_at}: ${message.content}</p>`
        currentChat.lastChild.scrollIntoView();
    } else {
        // if it's for a room we've joined but aren't viewing, we add or increment the badge next to the room
        newSpan = document.querySelector("#newFor" + roomFor)
        console.log(newSpan)
        if (newSpan.innerText == "") {
            newSpan.innerText = '1';
        } else {
            newSpan.innerText++;
        }
    }
})

//if a user joins the room we're viewing, this displays that in the chat
socket.on('user_join', (username, room) => {
    console.log(username + " joined " + room)
    if (room == currentRoom) {
        currentChat.innerHTML += `<p>${username} has joined us live</p>`
        currentChat.lastChild.scrollIntoView();
    }
})

//if a user leaves the room we're viewing, this displays that in the chat
socket.on('user_leave', (username, room) => {
    console.log(username + " left " + room)
    if (room == currentRoom) {
        currentChat.innerHTML += `<p>${username} has disconnected</p>`
        currentChat.lastChild.scrollIntoView();
    }
})


