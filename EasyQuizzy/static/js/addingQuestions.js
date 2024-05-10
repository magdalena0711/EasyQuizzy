

$(document).ready(function(){

    let initialized = false;

    function initialTable(){
        let vals = ["Redni broj", "Tekst", "Težina", "Tačan odgovor", "Netačan odgovor", "Netačan odgovor", "Netačan odgovor", "Izaberite"]
        for(let i = 0; i < vals.length; i++){
            $("#headCategories").append(
                $("<th></th>").text(vals[i]).attr("class", "catHeaders")
            );
        }
        
    }

    function changeRadio(start_id){
        console.log(start_id);
        $("#idPit").val(start_id);
        console.log($("#idPit").text());
        let values = [];
        let weight = ['easy', 'medium', 'hard'];
        for(let i = 0; i < 6; i++){
            values[i] = $("#"+start_id+i).text();
        }
        console.log(values)
        $("#textCat").val(values[0]);
        let weightNum = weight[parseInt(values[1])-1];
        console.log(weightNum);
        $("#"+weightNum).prop("checked", true);
        $("#correctCat").val(values[2]);
        $("#incorrect1Cat").val(values[3]);
        $("#incorrect2Cat").val(values[4]);
        $("#incorrect3Cat").val(values[5]);
    }

    $(".dugmici").click(function(){
        var id = $(this).attr("id");
        $.ajax({
            url: '/easyquizzy/getQuestionsByCategory',
            method: 'GET',
            headers:{
                "Content-Type": "application/json"
            },
            data: {'name': id},
            success: function(response){
                data = JSON.parse(response['questions'])

                if(initialized == false){
                    initialTable();
                    initialized = true;
                }
                
                $(".catQuestions").remove();
                
                for(let elem in data){
                    
                    let row = $("<tr></tr>").attr("class", "catQuestions").append(
                        $("<td></td>").text(elem+".")
                    )
                    for(let i = 0; i < data[elem].length - 1; i++){
                        row.append(
                            $("<td></td>").text(data[elem][i]).attr("id", (data[elem][data[elem].length-1]) + "" + i)
                        )
                    }
                    row.append(
                        $("<td></td>").attr("id", (data[elem][data[elem].length-1]) + "6").append($("<input type='radio'>").attr("name", "choice")).attr("class", "radioCat").change(
                            function(){
                                let tdOuter = $(this).closest('td');
                                let start_id = tdOuter.attr("id");
                                start_id = start_id.substring(0, start_id.length-1);
                                changeRadio(start_id);
                            }
                        )
                    )
                    $("#bodyCategories").append(row);
                }

                $("#tableCategory").css("display", "table");
                
            }
        });
    });

    $(".radioPermitted").change(function(){
        let tdRadio = $(this).closest('td');
        let id = tdRadio.attr("id");
        id = id.substring(0, id.length-1);
        let text = $("#"+id+8).text();
        $("#textPermitted").val(text);
    });

    

   
});