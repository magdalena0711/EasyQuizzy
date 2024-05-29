//Elena Savić 21/0332
//Petar Milojević 21/0336
//Ilija Miletić 21/0335
//Magdalena Obradović 21/0304
$(document).ready(function(){
    //funkcija za koja formira csrf token za AJAX zahtev
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

    // answered se u početku stavlja na false; njegova vrednost se stavlja na true kada se odgovori, a resetuje se kada stigne novo pitanje
    let socket = null;
    let answered = false;
    let replaced = false;
    let disabledAnswers = []
    $("#doneForm").css("display", "none");
    // uzimanje svog korisničkog imena sa stranice i korisničkog imena drugog igrača iz LocalStorage-a
    let username = $("#kor").text();
    let otherUsername = localStorage.getItem("drugi");
    $("#myInfo").text(username);
    $("#otherInfo").text(otherUsername);
    // formiranje WebSocket-a vezanog za PlayerGame consumer-a
    let roomName = localStorage.getItem("roomName");
    socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/easyquizzy/nextMultiplayer/'
        + roomName
        + '/'
    );
    socket.onopen = function(event) {
        // ispisivanje poruke prilikom otvaranja WebSocket-a
        console.log('WebSocket connection established.');
        
    }

    $(".answerClick").click(function(){
        // boldovanje odgovora prilikom klika i slanje odgovora, poena, trenutnog pitanja i korisničkog imena na server
        console.log(answered);
        if (answered == true) return;
        
        answered = true;
        let answer = $(this).val();
        $(this).css('font-weight', 'bolder');
        console.log($(this).css('text-weight'));
        
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
        // primanje poruke sa servera
        // ukoliko se u poruci nalazi korisničko ime znači da su obojica odgovorila i da stanje na stranici treba da se promeni
        // u suprotnom je stiglo novo pitanje sa novim odgovorima jer je izabrana zamena pitanja
        const data = JSON.parse(event.data);
        console.log(data);
        if(username in data){
            $("#myPoints").text(data[username][1])
            $("#otherPoints").text(data[otherUsername][1])
            let table = $("#tableAnswer");
            let trs = table.find("tr");
            let startIndex = 0;
            // obeležavanje tačnog odgovora zelenom bojom
            // obeležavanje svog netačnog odgovora žutom bojom
            // obeležavanje netačnog odgovora drugog igrača crnom bojom
            // ukoliko su oba igrča odgovorila netačno odgovor je obojen žuto-crno
            trs.each(function(index){
                let tds = $(this).find("td");
                startIndex = index;
                tds.each(function(index){
                    let btnIndex = startIndex * 2 + index;
                    console.log(btnIndex);
                    let btn = $("#answer"+btnIndex);
                    $("#answer"+btnIndex).css('font-weight', 'normal');
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
                // nakon što oba igrača vide stanje posle odgovaranja na pitanje resetuju se boje svih odgovora
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
                // ukoliko je bila korišćena pomoć pola-pola atribut disabled se stavlja na false za oba otklonjena odgovora
                if (disabledAnswers.length > 0){
                    for(let i = 0; i < disabledAnswers.length; i++){
                        
                        $("#answer"+disabledAnswers[i]).attr("disabled", false);
                        
                    }
                    disabledAnswers = [];
                }
                // slanje AJAX zahteva za dobijanje sledećeg pitanja
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
                            // učitavanje rednog broja pitanja, teksta i odgovora
                            $("#indexQuestion").text("Pitanje " + response['current_number']);
                            $("#questionText").text(response['question']);
                            let table = $("#tableAnswer");
                            let trs = table.find("tr");
                            let startIndex = 0;
                            console.log(response['answers'])
                            // svakom dugmetu se pristupa preko njegovog id-ja i postavlja mu se novi tekst
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
                            // ukoliko je prethodno pitanje bilo poslednje čuvaju se poeni u LocalStorage-u i korisničko ime
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
            // u slučaju dobijanja poruke da je došlo do zamene učitavaju se tekst novog pitanja i odgovori
            // answered se resetuje kako bi moglo da se odgovori na novo pitanje
            // oba igrača bivaju obaveštena o tome da je došlo do zamene
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
                    $("#answer"+btnIndex).css('background-color', "#0d6efd").css('font-weight', 'normal');
                    
                })

            })
            alert('Pitanje je zamenjeno!');
        }
 
        
    }

    $("#fifty_fifty").click(function(){
        // pomoć pola-pola ne može da se iskoristi ukoliko je već izabran neki odgovor
        // šalje se AJAX zahtev koji vraća tačan odgovor i onda se biraju dva netačna odgovora čiji atribut disabled postaje true
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
                // izbor dva random netačna odgovora
                // svako dugme ima id answer + broj od 0 do 3
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
        // zamena pitanja je omogućena ukoliko korisnik nije već zamenio pitanje i ukoliko nije već odgovorio
        if (replaced == true) return;
        if (answered == true) return;
        replaced = true;
        // šalje se poruka na server da treba da dođe do zamene pitanja
        socket.send("replace");
    })

    

    
});