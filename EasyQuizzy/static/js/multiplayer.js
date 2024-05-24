function submitForm() {
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

    $("#izbor_multi").change(function(){
        if ($("#roomCode").css("display") === "none") {
            $("#roomCode").css("display", "block");
        } else {
            $("#roomCode").css("display", "none");
        }

    })


});

