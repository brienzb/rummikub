function getCookieValue(name) {
    let cookieArr = document.cookie.split(";");

    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");

        if(name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }

    return null;
}

$(document).ready(function () {
    // TODO: 방 접속한 뒤, 필요 로직 구현
    let client_id = getCookieValue("RUMMIKUB_USER_ID");
    if (client_id === null) {
        client_id = "temp_client_id";
    }
    document.querySelector("#ws-id").textContent = client_id;

    const ws = new WebSocket(`ws://localhost:8000/websocket/${client_id}`);
    ws.onmessage = function(event) {
        const messages = document.getElementById('messages');
        const message = document.createElement('li');
        const content = document.createTextNode(event.data);
        message.appendChild(content)
        messages.appendChild(message)
    };

    $("#sendMessage").click(function () {
        const input = document.getElementById("messageText");
        ws.send(input.value)
        input.value = ''
        event.preventDefault()
    });
});