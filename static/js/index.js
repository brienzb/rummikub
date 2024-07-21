$(document).ready(function () {
    // 방 만들기 버튼
    $("#createRoom").click(function () {
        fetch("/room/create", {method: "POST"})
        .then(response => response.json())
        .then(roomId => {
            console.log("Room ID:", roomId);
            window.location.href = `/room/${roomId}`
        })
    });

    // 방 접속하기 버튼
    // [TODO] 방 접속하기 버튼 클릭 함수 구현
});