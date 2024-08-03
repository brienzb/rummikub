let client = undefined;

$(document).ready(function () {
    // 이미 등록한 유저가 있는지 확인
    fetch("/user/get", {method: "GET"})
    .then(response => {
        if (response.status !== 200) throw new Error();
        return response.json();
    })
    .then(user => {
        client = user;
        $("#currentNickname").text(`현재 닉네임: ${client["nickname"]}`)
    })
    .catch(error => {});

    // 유저 생성 버튼
    $("#createUser").click(function () {
        // TODO: nickname 영어, 한글, 숫자만 입력 가능 하도록 예외 처리
        const nickname = $('#nickname').val();
        if (nickname.length === 0 || nickname.length > 20) {
            // TODO: alert Bootstrap 이용
            alert("닉네임이 너무 짧거나 깁니다 (최소 1자 이상, 최대 20자 이하)");
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
        });
    });

    // 방 만들기 버튼
    $("#createRoom").click(function () {
        fetch("/room/create", {method: "POST"})
        .then(response => {
            if (response.status !== 200) throw new Error();
            return response.json();
        })
        .then(roomId => {
            console.log("Room ID:", roomId);
            window.location.href = `/room/${roomId}`
        })
        .catch(error => {
            // TODO: alert Bootstrap 이용
            alert("유저를 먼저 생성해 주세요");
        });
    });

    // 방 접속하기 버튼
    // TODO: 방 접속하기 버튼 클릭 함수 구현
});