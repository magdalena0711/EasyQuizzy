
$(document).ready(function(){
    let username = localStorage.getItem("prvi");
    let usernameOther = localStorage.getItem("drugi");
    let myPoints = localStorage.getItem("myPoints");
    let otherPoints = localStorage.getItem("otherPoints");

    $("#myInfo").text(username);
    $("#otherInfo").text(usernameOther);
    $("#myPoints").text(myPoints);
    $("#otherPoints").text(otherPoints);
    $("#idMyUsername").text(username);

    localStorage.removeItem("prvi");
    localStorage.removeItem("drugi");
    localStorage.removeItem("myPoints");
    localStorage.removeItem("otherPoints");
    localStorage.removeItem("roomName");


});