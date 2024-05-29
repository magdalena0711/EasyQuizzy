//Elena Savić 21/0332
//Petar Milojević 21/0336
//Ilija Miletić 21/0335
//Magdalena Obradović 21/0304
$(document).ready(function(){
    //Kada završimo partiju, neophodno je
    //Obrisati sve podatke sačuvane u localStorage, da bi sledeći igrači
    //Koji budu koristili isti kod za sobu, ili pak
    //I isti igrači mogli da igraju sledeće partije
    let username = localStorage.getItem("prvi");
    let usernameOther = localStorage.getItem("drugi");
    let myPoints = localStorage.getItem("myPoints");
    let otherPoints = localStorage.getItem("otherPoints");

    $("#myInfo").text(username);
    $("#otherInfo").text(usernameOther);
    $("#myPoints").text(myPoints);
    $("#otherPoints").text(otherPoints);
    $("#idMyUsername").text(username);

    localStorage.removeItem("prvi");
    localStorage.removeItem("drugi");
    localStorage.removeItem("myPoints");
    localStorage.removeItem("otherPoints");
    localStorage.removeItem("roomName");


});