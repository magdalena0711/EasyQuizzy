//Elena Savić 21/0332
//Petar Milojević 21/0336
//Ilija Miletić 21/0335
//Magdalena Obradović 21/0304
$(document).ready(function(){
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

    let socket = null;
    let answered = false;
    let replaced = false;
    let disabledAnswers = []
    $("#doneForm").css("display", "none");
    let username = $("#kor").text();
    let otherUsername = localStorage.getItem("drugi");
    $("#myInfo").text(username);
    $("#otherInfo").text(otherUsername);
    let roomName = localStorage.getItem("roomName");
    socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/easyquizzy/nextMultiplayer/'
        + roomName
        + '/'
    );
    socket.onopen = function(event) {
        console.log('WebSocket connection established.');
        
    }

    $(".answerClick").click(function(){
        console.log(answered);
        if (answered == true) return;
        
        answered = true;
        let answer = $(this).val();
        
        let myContent = ({
            'answer': answer,
            'points': $("#myPoints").text(),
            'question': $("#questionText").text(),
            'username': username
        })
        console.log(myContent);
        socket.send(JSON.stringify(myContent));
        

        
        
    })

    socket.onmessage = function(event){
            
        const data = JSON.parse(event.data);
        console.log(data);
        if(username in data){
            $("#myPoints").text(data[username][1])
            $("#otherPoints").text(data[otherUsername][1])
            let table = $("#tableAnswer");
            let trs = table.find("tr");
            let startIndex = 0;
            trs.each(function(index){
                let tds = $(this).find("td");
                startIndex = index;
                tds.each(function(index){
                    let btnIndex = startIndex * 2 + index;
                    console.log(btnIndex);
                    let btn = $("#answer"+btnIndex);
                    if (btn.val() == data[username][2]){
                        btn.css({
                            "background-color": "green"
                        })
                    }
                    if (btn.val() == data[username][0] && btn.val() == data[otherUsername][0] && btn.val() != data[username][2]){
                        btn.css({
                            "background-image": "linear-gradient(to right, yellow 50%, black 50%"
                        })
                        
                    }else{
                        if (btn.val() == data[username][0] && btn.val() != data[username][2]){
                            btn.css({
                                'background-color': 'yellow'
                        });
                        }
                        if (btn.val() == data[otherUsername][0] && btn.val() != data[username][2]){
                            btn.css({
                                
                                'background-color': 'black'
                        });
                        }
                    }
                    
                
                    
                })
                
            })

            setTimeout(function(){
                let table = $("#tableAnswer");
                let trs = table.find("tr");
                let startIndex = 0;
                trs.each(function(index){
                    let tds = $(this).find("td");
                    startIndex = index;
                    tds.each(function(index){
                        let btnIndex = startIndex * 2 + index;
                        $("#answer"+btnIndex).css("background-image", "none").css('background-color', "#0d6efd");
                        
                    })
    
                })
                answered = false;
                console.log(disabledAnswers.length);
                console.log(disabledAnswers);
                if (disabledAnswers.length > 0){
                    for(let i = 0; i < disabledAnswers.length; i++){
                        
                        $("#answer"+disabledAnswers[i]).attr("disabled", false);
                        
                    }
                    disabledAnswers = [];
                }
                $.ajax({
                    url: '/easyquizzy/jumpNext',
                    method: 'POST',
                    headers:{
                        "X-CSRFToken": csrftoken,
                        "Content-Type": "application/json"
                    },
                    data: {'room_name': roomName},
                    success: function(response){
                        if (response['done'] == false){
                            $("#indexQuestion").text("Pitanje " + response['current_number']);
                            $("#questionText").text(response['question']);
                            let table = $("#tableAnswer");
                            let trs = table.find("tr");
                            let startIndex = 0;
                            console.log(response['answers'])
                            trs.each(function(index){
                                let tds = $(this).find("td");
                                startIndex = index;
                                tds.each(function(index){
                                    let btnIndex = startIndex * 2 + index;
                                    $("#answer"+btnIndex).val(response['answers'][btnIndex]);
                                    $("#answer"+btnIndex).css('background-color', "#0d6efd")
                                    
                                })
                
                            })

                        }else{
                            localStorage.setItem("prvi", username);
                            localStorage.setItem("myPoints", $("#myPoints").text());
                            localStorage.setItem("otherPoints", $("#otherPoints").text());
                            $("#inputPoints").val($("#myPoints").text())
                            $("#doneForm").submit();
                        }

                    }
                })
            }, 2000)


        }else{
            answered = false;
            console.log('zamena');
            if (replaced == true){
                $("#replace_question").attr("disabled", true);
            }
            console.log(data);
            $("#questionText").text(data['question']);
            let table = $("#tableAnswer");
            let trs = table.find("tr");
            let startIndex = 0;
            console.log(data['answers'])
            trs.each(function(index){
                let tds = $(this).find("td");
                startIndex = index;
                tds.each(function(index){
                    let btnIndex = startIndex * 2 + index;
                    $("#answer"+btnIndex).val(data['answers'][btnIndex]);
                    $("#answer"+btnIndex).css('background-color', "#0d6efd")
                    
                })

            })
            alert('Pitanje je zamenjeno!');
        }
 
        
    }

    $("#fifty_fifty").click(function(){
        if (answered == true) return;
        let decoded = decodeURIComponent($("#questionText").text());
        $.ajax({
            url: '/easyquizzy/getCorrect',
            method: 'POST',
            headers:{
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            },
            data: {'text': decoded},
            success: function(response){
                let correctAnswer = response['correct'];
                console.log(correctAnswer);
                let i = 0
                do{
                    let index = parseInt(Math.random() * 4);
                    console.log(index);
                    if ($("#answer"+index).val() != correctAnswer && disabledAnswers.includes(index) == false){
                        $("#answer"+index).css("background-color", "red").attr("disabled", true);
                        disabledAnswers.push(index);
                        i += 1;
                    }
                }while (i != 2);
                $("#fifty_fifty").attr("disabled", true);
            }
        })
    });

    $("#replace_question").click(function(){
        if (replaced == true) return;
        if (answered == true) return;
        replaced = true;
        socket.send("replace");
    })

    

    
});