function loadFilms()
{
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", "localhost:5000/films", true);
    xhttp.send();

    console.log(xhttp.responseText);

    table = document.getElementById("filmsTable");
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

