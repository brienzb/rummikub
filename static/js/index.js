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
    function createUser() {
        const nickname = $('#nickname').val();

        if (!isValidInput(nickname, 1, 20, false)) {
            $("#nickname").addClass("is-invalid");
            return;
        }
        $("#nickname").removeClass("is-invalid");

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
    }
    $("#nickname").on("keypress", function(event) { if (event.key === "Enter") createUser(); });
    $("#createUser").click(function () { createUser(); });

    // 방 만들기 버튼
    $("#createRoom").click(function () {
        const playUserCount = $("input[name='playUserCount']:checked").val();
        const turnTime = $("#turnTime").val();

        fetch("/room/create", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "playUserCount": parseInt(playUserCount, 10),
                "turnTime": parseInt(turnTime, 10),
            }),
        })
            .then(response => {
                if (response.status !== 200) {
                    const error = new Error();
                    error.response =  response;
                    throw error;
                }
                return response.json();
            })
            .then(roomId => {
                window.location.href = `/room/${roomId}`
            })
            .catch(error => {
                if (error.response.status === 403) showAlert("닉네임을 먼저 생성해 주세요");
                else showAlert("예기치 못한 에러 입니다");
            });
    });

    // 방 접속하기 버튼
    function enterRoom() {
        const roomId = $("#roomId").val();

        if (!isValidInput(roomId, 16, 16)) {
            $("#roomId").addClass("is-invalid");
            return;
        }
        $("#roomId").removeClass("is-invalid");

        fetch("/room/join", {
            method: "POST",
            headers: {"Content-Type": "text/plain"},
            body: roomId,
        })
            .then(response => {
                if (response.status !== 200) {
                    const error = new Error();
                    error.response =  response;
                    throw error;
                }
            })
            .then(() => {
                window.location.href = `/room/${roomId}`
            })
            .catch(error => {
                if (error.response.status === 403) showAlert("닉네임을 먼저 생성해 주세요");
                else showAlert("존재 하지 않는 방 입니다");
            });
    }
    $("#roomId").on("keypress", function(event) { if (event.key === "Enter") enterRoom(); });
    $("#enterRoom").click(function () { enterRoom(); });
});