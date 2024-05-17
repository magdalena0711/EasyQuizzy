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
    $('.odg').change(function (){
        let odgovor = $(this).val()
    })

     $("#slanje").click(function(){
         console.log("Kliknuo!")

        let tekst = $('#textQuestionDay').val()

        $.ajax({
            url: '/easyquizzy/dayQuestion',
            method: 'POST',
            headers:{
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            },
            data: {'tekstPitanja': tekst,
            'answer': odgovor},
            success: function(response){
                successfulRequest(response['message']);
                if(response['successful'] == true){
                    $("#"+username).closest('tr').remove();
                }
            }
        })

    });
})