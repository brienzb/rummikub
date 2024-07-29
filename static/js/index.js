let client = undefined;

$(document).ready(function () {
    // 유저 생성 버튼
    $("#createUser").click(function () {
        // TODO: nickname 영어, 한글, 숫자만 입력 가능 하도록 예외 처리
        const nickname = $('#nickname').val();
        if (nickname.length === 0 || nickname.length > 20) {
            // TODO: alert Bootstrap 이용
            alert("닉네임이 너무 짧거나 깁니다..");
            return;
        }

        fetch("/user/create", {
            method: "POST",
            headers: {"Content-Type": "text/plain"},
            body: nickname,
        })
        .then(response => response.json())
        .then(user => {
            client = user;

            $("#currentNickname").text(`현재 닉네임: ${client["nickname"]}`)
        })
    });

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
    // TODO: 방 접속하기 버튼 클릭 함수 구현
});