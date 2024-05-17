

$(document).ready(function(){

    var clickedRadio = null;

    function successfulRequest(message){
        var ale = $("#deleteAlert");
        if (ale.css("display") === "block") {
            ale.css("display", "none");
        }
        var errorDiv = $("#errorMessage");
        if(errorDiv.css("display") === "none"){
            errorDiv.css("display", "block");
            errorDiv.css({
                "width": "100%",
                "height": "30%",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center"
            })
        }
        $("#succ").text(message);
        $("#succ").css({
            "font-style": "italic",
            'font-size': "80%",
            'font-weight': 'bold'
        });
        clickedRadio = null;
        $("#"+username).prop("checked", false);
        $("#inputUser").attr("disabled", false);
        setInterval(function(){
            $("#succ").text("");
            errorDiv.css("display", "none");
            
        },2000);
    };

    $("#deleteButton").click(function(){
        var ale = $("#deleteAlert");
        if (ale.css("display") === "none") {
          ale.css("display", "block");
        } else {
          ale.css("display", "none");
        }
    });

    $("#noButton").click(function(){
        var ale = $("#deleteAlert")
        if (ale.css("display") === "none") {
            ale.css("display", "block"); 
        } else {
            ale.css("display", "none"); 
        }
    });

    $(".userRadios").change(function(){
        if ($(this).is(':checked')){
            clickedRadio = $(this);
        }
        $("#inputUser").attr("disabled", true);
    });

    $("#inputUser").on({
        focus: function(){
            $(".userRadios").attr("disabled", true);
        },
        blur: function(){
            if($("#inputUser").val() == ''){
                $(".userRadios").attr("disabled", false);
            }
            
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function get_user(){
        var username = null;
        if(clickedRadio != null){
            username = clickedRadio.attr("id");
            clickedRadio = null;
        }else if($("#inputUser").val() != ''){
            username = $("#inputUser").val();
        }
        return username;
    }

    $("#yesButton").click(function(){
        msg = "Niste izabrali korisnika koga želite da obrišete";
        username = get_user();
        if (username == null){
            successfulRequest(msg);
            return;
        }

        $.ajax({
            url: '/easyquizzy/delete',
            method: 'POST',
            headers:{
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            },
            data: {'username': username},
            success: function(response){
                successfulRequest(response['message']);
                if(response['successful'] == true){
                    $("#"+username).closest('tr').remove();
                }
            }
        })

    });

    $("#moderatorButton").click(function(){
        msg = "Niste izabrali korisnika koga želite postavite za moderatora";
        username = get_user();
        if (username == null){
            successfulRequest(msg);
            return;
        }
        

        $.ajax({
            url: '/easyquizzy/addModerator',
            method: 'POST',
            headers:{
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            },
            data: {'username': username},
            success: function(response){
                successfulRequest(response['message']);
                if(response['successful'] == true){
                    $("#role"+username).text('moderator');
                }
            }
        })
    });
    

    
});