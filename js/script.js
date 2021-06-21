function getFilmsWithPermissions()
{
    const xhttp = new XMLHttpRequest();

    xhttp.open("GET", "https://localhost:5000/filmsWithPermissions", true);
    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 200) {
            table = document.getElementById("filmsTable");
            
            var data = JSON.parse(this.responseText);

            for(var i =0;i< data.length;i++)
            {
                element = data[i];

                var row = table.insertRow(-1);

                var id = row.insertCell(0);

                var name = row.insertCell(1);

                var read = row.insertCell(2);
                var read_button = row.insertCell(3);

                var write = row.insertCell(4);
                var edit_button = row.insertCell(5);
                var delete_button = row.insertCell(6)

                var delegation = row.insertCell(7);

                var ownership = row.insertCell(8);


                id.innerHTML = element.id;
                name.innerHTML = element.title;
                read.innerHTML = createCheckbox(element.read);
                read_button.innerHTML = createButton(element.read,element.id)
                write.innerHTML = createCheckbox(element.write);
                edit_button.innerHTML = createButton(element.write,element.id)
                delete_button.innerHTML = createButton(element.write,element.id)
                delegation.innerHTML = createCheckbox(element.delegation)
                ownership.innerHTML = createCheckbox(element.ownership);
            }
 
            // we get the returned data
        }
        // end of state change: it can be after some time (async)
    };

    xhttp.send();
}

function getFilms()
{
    const xhttp = new XMLHttpRequest();

    xhttp.open("GET", "https://localhost:5000/films", true);
    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 200) {
            table = document.getElementById("filmsTable");
            
            var data = JSON.parse(this.responseText);

            for(var i =0;i< data.length;i++)
            {
                element = data[i];

                var row = table.insertRow(-1);

                var id = row.insertCell(0);
                var name = row.insertCell(1);
                var choice = row.insertCell(2);

                id.innerHTML = element.id;
                name.innerHTML = element.title;
                choice.innerHTML = "<input type=\"radio\" name =\"filmChoice\" value=\""+element.id+"\"/>";

            }
 
            // we get the returned data
        }
        // end of state change: it can be after some time (async)
    };

    xhttp.send();
}

function getUsers()
{
    const xhttp = new XMLHttpRequest();

    xhttp.open("GET", "https://localhost:5000/users", true);
    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 200) {
            table = document.getElementById("usersTable");
            
            var data = JSON.parse(this.responseText);

            for(var i =0;i< data.length;i++)
            {
                element = data[i];

                var row = table.insertRow(-1);

                var name = row.insertCell(0);
                var choice = row.insertCell(1);

                name.innerHTML = element.username;
                choice.innerHTML = "<input type=\"radio\" name =\"userChoice\" value=\""+element.username+"\"/>";

            }
 
            // we get the returned data
        }
        // end of state change: it can be after some time (async)
    };

    xhttp.send();
}

function setPermissions()
{
    const filmChoice = document.querySelector('input[name="filmChoice"]:checked')
    const userChoice = document.querySelector('input[name="userChoice"]:checked')

    const read = document.getElementById("read").checked;
    const write = document.getElementById("write").checked;
    const delegation = document.getElementById("delegation").checked;
    const ownership = document.getElementById("ownership").checked;



    if(ownership == false && filmChoice != null && userChoice != null )
    {
        
        const filmId = filmChoice.value
        const username = userChoice.value
        
        const xhttp = new XMLHttpRequest();
        
        xhttp.open("POST", "https://localhost:5000/permissions", true);
        xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');
        xhttp.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        xhttp.onreadystatechange = function () {
            if (this.readyState != 4) return;
        
            if (this.status == 200) {
                return;
                
    
                // we get the returned data
            }
            // end of state change: it can be after some time (async)
        };

        var req = {
            "id":filmId,
            "username2":username,
            "read":read,
            "write":write,
            "delegation":delegation,
        };

        xhttp.send(JSON.stringify(req));
    }
    else if(ownership == true && filmChoice != null && userChoice != null)
    {
const filmId = filmChoice.value
        const username = userChoice.value
        
        const xhttp = new XMLHttpRequest();
        
        xhttp.open("POST", "https://localhost:5000/transfer", true);
        xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');
        xhttp.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        xhttp.onreadystatechange = function () {
            if (this.readyState != 4) return;
        
            if (this.status == 200) {
                return;
                
    
                // we get the returned data
            }
            // end of state change: it can be after some time (async)
        };

        var req = {
            "id":filmId,
            "username2":username,
            "read":read,
            "write":write,
            "delegation":delegation,
        };

        xhttp.send(JSON.stringify(req));
    }

}

/*
function getFilm()
{
    const xhttp = new XMLHttpRequest();



    xhttp.open("GET", "https://localhost:5000/film/", true);
    xhttp.setRequestHeader('Access-Control-Allow-Origin', '*');

    xhttp.onreadystatechange = function () {
        if (this.readyState != 4) return;
    
        if (this.status == 200) {
            table = document.getElementById("filmsTable");
            
            var data = JSON.parse(this.responseText);

            for(var i =0;i< data.length;i++)
            {
                element = data[i];

                var row = table.insertRow(-1);

                var id = row.insertCell(0);

                var name = row.insertCell(1);

                var read = row.insertCell(2);
                var read_button = row.insertCell(3);

                var write = row.insertCell(4);
                var edit_button = row.insertCell(5);
                var delete_button = row.insertCell(6)

                var delegation = row.insertCell(7);

                var ownership = row.insertCell(8);


                id.innerHTML = element.id;
                name.innerHTML = element.title;
                read.innerHTML = createCheckbox(element.read);
                read_button.innerHTML = createButton(element.read,element.id)
                write.innerHTML = createCheckbox(element.write);
                edit_button.innerHTML = createButton(element.write,element.id)
                delete_button.innerHTML = createButton(element.write,element.id)
                delegation.innerHTML = createCheckbox(element.delegation)
                ownership.innerHTML = createCheckbox(element.ownership);
            }
 
            // we get the returned data
        }
        // end of state change: it can be after some time (async)
    };

    xhttp.send();
}
*/
function createCheckbox(checked)
{
    if(checked == null || checked == false)
    {
        return "<input type=\"checkbox\" disabled=\"true\" />"
    }
    else if(checked==true)
    {
        return "<input type=\"checkbox\" checked disabled=\"true\" />"
    }
}

function createButton(disabled, id)
{
    if(disabled == null || disabled == false)
    {
        return "<button disabled=\"true\" class=\"notUsableButton\"/>"
    }
    else if(disabled==true)
    {
        return "<button class=\"usableButton\"><a href=\"https://localhost:5000/film/"+id+"\">X</a></button>"
    }
}