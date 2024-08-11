const rummikubServerHost = "localhost:8000";
const userCookieKey = "RUMMIKUB_USER_ID"

function getCookieValue(cookie_key) {
    let cookieArr = document.cookie.split(";");

    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if(cookie_key === cookiePair[0].trim()) return decodeURIComponent(cookiePair[1]);
    }

    return null;
}

function parseAfterPath(url, path) {
    const regex = new RegExp('/' + path + '/([^/]+)');

    const match = url.match(regex);
    if (match) return match[1];

    return null
}

function isValidInput(inputValue, minLength, maxLength, checkValidPattern = true) {
    const validPattern = /^[A-Za-z0-9]+$/;

    if (checkValidPattern && !validPattern.test(inputValue)) return false;
    return (inputValue.length >= minLength && inputValue.length <= maxLength);
}

function getUserId() { return getCookieValue(userCookieKey); }
function getRoomId() { return parseAfterPath(window.location.href, "room"); }