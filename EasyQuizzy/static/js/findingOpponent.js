//Elena Savić 21/0332
//Petar Milojević 21/0336
//Ilija Miletić 21/0335
//Magdalena Obradović 21/0304

$(document).ready(function(){
    /*
    Kada igrač uđe u određenu sobu, kreće odbrojavanje vremena koje čeka na suparnika
    U bilo kom trenutku može da prekine pretragu
    Tokom pretrage se otvara webSocket koji će se zatvoriti kada dva igrača uđu u istu sobu, tj. kada se spoje
    */ 
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
    /*
    Da bi igrač znao sa kim je spojen, u localStorage će sačuvati korisničko ime drugog igrača
    */ 
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