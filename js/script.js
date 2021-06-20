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
            console.log(data);
            for(var i =0;i< data.length;i++)
            {
                element = data[i];

                var row = table.insertRow(-1);

                var id = row.insertCell(0);
                var name = row.insertCell(1);
                var time = row.insertCell(2);
                var read = row.insertCell(3);
                var write = row.insertCell(4);
                var owner = row.insertCell(5);

                id.innerHTML = element.id;
                name.innerHTML = element.title;
                time.innerHTML = element.time;
                read.innerHTML = createCheckbox(element.read);
                write.innerHTML = createCheckbox(element.write);
                owner.innerHTML = createCheckbox(element.owner);
            }
 
            // we get the returned data
        }
        // end of state change: it can be after some time (async)
    };

    xhttp.send();
}

function createCheckbox(checked)
{
    if(checked == true)
    {
        return "<input type=\"checkbox\" checked=\"true\" disabled=\"true\">"
    }
    else
    {
        return "<input type=\"checkbox\" checked=\"false\" disabled=\"true\">"
    }
}