let client = undefined;
let userId = getUserId();
let roomId = getRoomId();

$(document).ready(function () {
    fetch("/user/get", {method: "GET"})
        .then(response => {
            if (response.status !== 200) throw new Error();
            return response.json();
        })
        .then(user => {
            client = user;
            $("#ws-client").text(`${client["nickname"]} (${client["user_id"]})`);
        })
        .catch(error => {
            alert("잘못된 접근 입니다");
            window.history.back();
        });

    // TODO: 방 접속한 뒤, 필요 로직 구현
    const ws = new WebSocket(`ws://${rummikubServerHost}/websocket/${roomId}/${userId}`);
    ws.onmessage = function(event) {
        const messages = document.getElementById('messages');
        const message = document.createElement('li');
        const content = document.createTextNode(event.data);
        message.appendChild(content)
        messages.appendChild(message)
    };

    function sendMessage() {
        const input = document.getElementById("messageText");
        ws.send(input.value)
        input.value = ''
        event.preventDefault()
    }
    $("#messageText").on("keypress", function(event) { if (event.key === "Enter") sendMessage(); });
    $("#sendMessage").click(function () { sendMessage() });
});