
// function loaded(){
//     document.getElementById("formStart").addEventListener("submit", function(event){
//         event.preventDefault();
//         this.action = "nextMultiplayer/" + roomName + "/";
//         alert(this.action);
//         console.log(this.action);
//
//         this.submit();
//     })
// }


$(document).ready(function(){


    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    const korIme = " " + $("#kor").text();
    console.log(roomName)
    console.log(korIme)
    const socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/easyquizzy/finding/'
            + roomName
            + '/'
    );
    localStorage.setItem("roomName", roomName);
    socket.onopen = function(event) {
        console.log('WebSocket connection established.');
    }


    let form = $("#formStart");

    form.submit(function(event){
        this.action = "/easyquizzy/nextMultiplayer/" + roomName + "/";
        alert(this.action);

        this.submit();
    });

    socket.onmessage = function(event){
        const data = event.data;
        console.log(roomName);
        $("#nextPageMulti").click();

    };


});