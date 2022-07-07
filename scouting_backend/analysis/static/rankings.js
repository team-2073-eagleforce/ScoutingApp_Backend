let prev_clicked = null
let prev_table = null

let has_auto_clicked = false;
let has_teleop_clicked = false;
let has_climb_clicked = false;
let has_total_clicked = false;

document.getElementById("auto").style.display = "none"
document.getElementById("teleop").style.display = "none"
document.getElementById("climb").style.display = "none"
document.getElementById("total").style.display = "none"

document.getElementById("by_auto").onclick = () => {
    selector("by_auto", has_auto_clicked, "auto")
    has_auto_clicked = true;
}
document.getElementById("by_teleop").onclick = () => {
    selector("by_teleop", has_teleop_clicked, "teleop")
    has_teleop_clicked = true;
}
document.getElementById("by_climb").onclick = () => {
    selector("by_climb", has_climb_clicked, "climb")
    has_climb_clicked = true;
}
document.getElementById("by_total").onclick = () => {
    selector("by_total", has_total_clicked, "total")
    has_total_clicked = true;
}

function selector(sortby, has_been_clicked, table_type) {
    if (prev_clicked !== null) {
        document.getElementById(prev_clicked).style = ""
        document.getElementById(prev_table).style.display = "none"
    }
    document.getElementById(sortby).style = "background-color: red;"
    prev_clicked = sortby
    prev_table = table_type

    if (has_been_clicked) {
        document.getElementById(table_type).style.display = "table"
    } else {
        $.post("/analysis/sorter", {
            button_selected: sortby
        }, function (data) {
            for (let i = 0; i < Object.keys(data).length; i++) {
                var tr = document.createElement("TR");
                var teamTd = document.createElement("TD");
                var scoreTd = document.createElement("TD");
                teamTd.innerText = Object.keys(data)[i];
                scoreTd.innerText = data[Object.keys(data)[i]];
                teamTd.setAttribute("scope", "row")
                tr.appendChild(teamTd)
                tr.appendChild(scoreTd)
                tr.setAttribute("class", "generated")
                document.getElementById(table_type).appendChild(tr)

                sortTable(table_type)
                document.getElementById(table_type).style.display = "table"
            }
        });
    }
}

function sortTable(table_to_sort) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById(table_to_sort);
    switching = true;

    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[1];
            y = rows[i + 1].getElementsByTagName("TD")[1];
            // Check if the two rows should switch place:
            if (parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}