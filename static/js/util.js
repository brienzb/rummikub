function isValidInput(inputValue, minLength, maxLength, checkValidPattern = true) {
    const validPattern = /^[A-Za-z0-9]+$/;

    if (checkValidPattern && !validPattern.test(inputValue)) return false;
    return (inputValue.length >= minLength && inputValue.length <= maxLength);
}