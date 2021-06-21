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
        return "<button class=\"usableButton\"><a href=\""+id+"\"></a></button>"
    }
}