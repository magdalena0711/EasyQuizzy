
$(document).ready(function(){

    $(".dugmici").change(function(){
        id = $(this).attr("id");
        $("#catName").val(id);

    });

    $("#add").css("display", "block");
    $("#edit").css("display", "block");


});