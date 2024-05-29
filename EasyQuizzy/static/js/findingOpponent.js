

$(document).ready(function(){

    let searchTime = 1;
    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    const korIme = $("#kor").text();
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
        socket.send(korIme);
    }


    let form = $("#formStart");

    form.submit(function(event){
        this.action = "/easyquizzy/nextMultiplayer/" + roomName + "/";
        this.submit();
    });

    socket.onmessage = function(event){
        const data = JSON.parse(event.data);
        
        if ("first" in data){
            let username1 = data['first'];
            let username2 = data['second'];
            if (username1 != korIme){
                localStorage.setItem("drugi", username1);
            }else{
                localStorage.setItem("drugi", username2);
            }
            console.log(roomName);
            $("#nextPageMulti").click();
        }else{
            alert('Soba je zauzeta! Izađite i uđite u neku drugu sobu!')
        }
        

    };

    setInterval(function(){
        console.log('usao');
        searchTime += 1;
        
        $("#searchTime").text("Vreme pretrage: " + searchTime);
    }, 1000);

    


});