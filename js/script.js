function getFilms()
{
    const xhttp = new XMLHttpRequest();

    xhttp.open("GET", "https://localhost:5000/films", true);

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 200) {
            var data = JSON.parse(this.responseText);
            console.log(data);
            // we get the returned data
        }
        // end of state change: it can be after some time (async)
    };

    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        username: "123",
        password: "123"
    }));

    

    table = document.getElementById("filmsTable");

    //for
    var row = table.insertRow(-1);

    var name = row.insertCell(0);
    var time = row.insertCell(1);
    var read = row.insertCell(2);
    var write = row.insertCell(3);
    var owner = row.insertCell(4);

    name.innerHTML = "NEW CELL1";
    time.innerHTML = "NEW CELL2";
    read.innerHTML = "<input type=\"checkbox\" disabled=\"true\">";
    write.innerHTML = "NEW CELL2";
    owner.innerHTML = "NEW CELL2";
}

async function log_in()
{
    var login = document.getElementById("login").value;
    var password = await hash(document.getElementById("password").value)
    
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "https://localhost:5000/login", true);
    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhttp.setRequestHeader('Content-Type', 'application/json');

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 302) {
            console.log(this.responseURL)
            // we get the returned data
        }
    
        // end of state change: it can be after some time (async)
    };

    xhttp.send(JSON.stringify({
        username: login,
        password: password
    }));

    
}

async function hash(password)
{
    const msgUint8 = new TextEncoder().encode(password);                           // encode as (utf-8) Uint8Array
    const hashBuffer = await crypto.subtle.digest('SHA-512', msgUint8);           // hash the message
    const hashArray = Array.from(new Uint8Array(hashBuffer));                     // convert buffer to byte array
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); // convert bytes to hex string
    return hashHex;
}

async function register()
{
    
    var login = document.getElementById("login").value;
    var password = await hash(document.getElementById("password").value)
    
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "https://localhost:5000/users", true);
    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhttp.setRequestHeader('Content-Type', 'application/json');

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 200) {
            var data = JSON.parse(this.responseText);
            console.log(data)
            // we get the returned data
        }
    
        // end of state change: it can be after some time (async)
    };

    xhttp.send(JSON.stringify({
        username: login,
        password: password
    }));
}

function set_film()
{

}

function set_permission()
{

}

function logout()
{

}