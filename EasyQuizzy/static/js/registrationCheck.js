function checkPassword(){
    let password = document.getElementById("password").value;
    if(/^.{8,}$/.test(password) == false){
        alert("Lozinka mora sadržati barem 8 karaktera!");
    }
    if(/[a-z]/.test(password) == false){
        alert("Lozinka mora sadržati barem jedno malo slovo!");
    }
    if(/[0-9]/.test(password) == false){
        alert("Lozinka mora sadržati barem jednu cifru!");
    }
    let passwordSecond = document.getElementById("passwordVal").value;
    if(password != passwordSecond){
        alert("Lozinke se ne poklapaju!");
    }
}
