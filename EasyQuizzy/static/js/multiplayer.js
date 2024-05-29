//Elena Savić 21/0332
//Petar Milojević 21/0336
//Ilija Miletić 21/0335
//Magdalena Obradović 21/0304
function submitForm() {
        /*
        Kada se korisnik pojavi na stranici za izbor testa, ima dva izbora
        Ili će igrati samostalo tj. singleplayer opcija
        Ili će igrati protiv nekoga, tj. multiplayer opcija
        */ 

        var single_izbor = document.getElementById('izbor_single').checked;
        var multi_izbor = document.getElementById('izbor_multi').checked;
        if(!single_izbor && !multi_izbor)
        {
            alert("Niste izabrali nijednu opciju,pa ne mozete dalje!");
        }else
        {
            document.getElementById('nastavi_dalje').submit();
        }
    }


$(document).ready(function(){
    $("#roomCode").css("display", "none");
    let form = document.getElementById("multiUpdate");
    form.onsubmit = function(event){
        let roomName = $("#code").val();
        console.log(roomName);
        this.action = "finding/" + roomName + "/";
        console.log(this.action);

        this.submit();
    }
    /* 
    Ako igrač izabere muliplayer opciju, pojaviće mu se tektualno polje za upis koda sobe kojoj želi da pristupi, koje će do tada biti skriveno
    */
    $("#izbor_multi").change(function(){
        if ($("#roomCode").css("display") === "none") {
            $("#roomCode").css("display", "block");
        } else {
            $("#roomCode").css("display", "none");
        }

    })


});

