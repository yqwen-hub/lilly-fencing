function checkPassword() {

    var password = document.getElementById("pwd").value;

    if (password === "fencing123") {
        window.location.href = "videos.html";
    } else {
        document.getElementById("error").innerText = "Wrong password";
    }

}