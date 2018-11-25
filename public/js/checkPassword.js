function checkPassword() {
    var p1 = document.getElementById('password').value;
    var p2 = document.getElementById('confirmPassword').value;
    var isMatch = p1 === p2;
    if (!isMatch){
        alert('Password not match, please check again!');
    }
    return isMatch;
}