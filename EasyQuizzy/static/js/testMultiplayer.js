
$(document).ready(function(){
    let username = $("#kor").text();
    $(".answerClick").click(function(){
        alert('usao');
        let answer = $(this).text();
        let roomName = localStorage.getItem("roomName");
        const socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/easyquizzy/nextMultiplayer/'
            + roomName
            + '/'
        );
        socket.onopen = function(event) {
            console.log('WebSocket connection established.');
        }
    })
});